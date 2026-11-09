# Phase 2: GitOps with Argo CD

## The idea
Until now, we changed the cluster by running `kubectl apply`. That is **push**: a person pushes changes in. Nothing stops the cluster and Git from disagreeing (we saw that drift with the ConfigMap).

GitOps flips it. Git is the source of truth. An agent inside the cluster, **Argo CD**, **pulls** from Git and makes the cluster match. This is a second reconcile loop:
- Loop 1 (Kubernetes): objects in the cluster -> running pods.
- Loop 2 (Argo CD): files in Git -> objects in the cluster.

Argo CD does the CD part (delivery). It does not build or test anything, which is the CI part.

## What we installed
Argo CD v3.6.1, vendored in `manifests/phase2/argocd/`, with a kustomize patch that turns off two parts we don't need (dex for single sign-on, and the notifications controller) to save memory on an 8 GB laptop. The running parts:
- `argocd-server`: the API and web UI.
- `argocd-repo-server`: fetches the Git repo and renders the YAML.
- `argocd-application-controller`: the loop. It compares Git to the cluster and syncs.
- `argocd-redis`: a cache.
- `argocd-applicationset-controller`: generates Applications from templates (unused).

## The Application
An **Application** tells Argo CD what to watch. Ours (`manifests/phase2/applications/platform-app.yaml`) says: "watch the folder `deploy/app` on branch `main` of this repo, and make the `default` namespace match it." The repo is public, so no credentials were needed.

`deploy/app/` holds only the backend and frontend. The demo files from Phase 1 stay in `manifests/phase1/`, because Argo CD syncs a whole folder.

Argo CD pulls from GitHub, not from your laptop. A change only counts once it is pushed.

## What we saw
1. **Right after creating the Application:** `OutOfSync` and `Missing`. Argo CD saw that Git wanted 5 resources and the cluster had none. It did nothing, because sync was manual.
2. **After one manual sync:** `Synced` and `Healthy`, with 4 pods. No `kubectl apply` for the app.
3. **Drift, with self-heal off:** we scaled the frontend from 2 to 5 by hand. Argo CD showed `Deployment/frontend OutOfSync` and left it at 5. It noticed but did not act.
4. **We turned on automated sync with self-heal and prune.**
5. **Drift, with self-heal on:** we scaled to 5 again. It went back to 2 in about 1.8 seconds.
6. **We deleted the backend Service by hand.** Argo CD recreated it in about 5.6 seconds.

These timings are from one run on a small laptop, so treat them as rough.

## A change made through Git
We edited `deploy/app/frontend.yaml` (replicas 2 to 3), committed, and pushed. Argo CD scaled the frontend to 3 about 80 seconds after the push, with no `kubectl` from us. The Application then showed `Synced` at that commit.

That is slower than the 2 seconds for a hand edit, for a reason:
- **A change in the cluster** is seen right away. Argo CD watches the cluster for events.
- **A change in Git** is found by **polling**. Argo CD asks GitHub "anything new?" on a timer. The default is about every 3 minutes, so a push can take anywhere from a moment to about 3 minutes to be noticed. Our 80 seconds is one sample of that range.

A **webhook** from GitHub can make it instant, but that needs GitHub to reach the cluster, which a local laptop cluster cannot offer. A manual refresh of the Application also works.

## The settings that matter
- **No sync policy:** Argo CD reports drift and waits.
- **`automated`:** Argo CD syncs when Git changes.
- **`selfHeal: true`:** Argo CD also reverts manual changes made in the cluster.
- **`prune: true`:** Argo CD deletes cluster objects that were removed from Git.

## Why this matters
- Git history becomes the record of what changed, who changed it, and when.
- Rolling back a bad change is a `git revert`.
- A manual hotfix in the cluster does not survive. That can surprise you in an outage, so a real team agrees on how to handle it.

## Remember
- Argo CD is a second reconcile loop: Git -> cluster.
- Pull, not push.
- Self-heal is a setting, off by default.
- Argo CD sees only what is pushed to GitHub.
- It reacts to cluster changes at once, but finds Git changes by polling.
