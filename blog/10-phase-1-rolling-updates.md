# Phase 1, step 4: Rolling updates and rollback

## The problem
You want to change the version of a running app without any downtime.

## How a Deployment does it
When you change the pod blueprint (for example the image), the Deployment:
1. Creates a **new ReplicaSet** for the new version.
2. Starts a new pod.
3. Waits until the new pod passes its **readiness probe**.
4. Stops one old pod.
5. Repeats until every pod is the new version.

The old ReplicaSet is kept, scaled to 0. That is what makes rollback quick.

Two settings control the speed (both default to 25%):
- `maxSurge`: how many extra pods may exist during the update.
- `maxUnavailable`: how many pods may be missing at once.

Readiness probes are what make this safe. A new pod gets traffic only after it says it is ready.

## What we tested: a broken update
We changed the image to `nginx:9.99-doesnotexist`, which does not exist.

Result after 20 seconds:
- 3 old pods: still `Running` and ready.
- 1 new pod: stuck in `ImagePullBackOff`. It never became ready.
- Deployment: `READY 3/3`, `UP-TO-DATE 1`.
- Requests through the Service: no failures.

The update stalled, and the app stayed up. Kubernetes never removed a working pod before a replacement was ready.

## Rolling back
We re-applied the committed manifest (the good image). The Deployment went back to the existing ReplicaSet with 3 pods. The three original pods were never touched, and the broken pod was removed. It took about a second.

Kubernetes also has `kubectl rollout undo deployment/hello`, which goes back to the previous version. We used the manifest instead, because in this project Git is the source of truth. Undoing with a command would leave the cluster different from Git.

## What to watch for
- A stuck update does not fix itself and does not send an alert. The status simply stays at `UP-TO-DATE 1` of 3. In Phase 4 we will add monitoring so this is visible.
- Without a readiness probe, Kubernetes would treat a new pod as ready as soon as its process started, and bad versions could take traffic.

## Remember
- New version in, old version out, one at a time.
- Readiness gates each step.
- A bad version stalls instead of breaking the app.
- Rollback is just going back to the previous ReplicaSet.
