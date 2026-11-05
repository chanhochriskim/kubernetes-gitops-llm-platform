# Phase 1, step 5: ConfigMaps and Secrets

## The problem
An app needs settings (a log level, a database address) and secrets (a password, an API key). They should not be baked into the image, or you would rebuild the image for every change. Passwords must never go into Git.

## Two objects
- **ConfigMap:** ordinary settings.
- **Secret:** sensitive values.

A pod can use either one in two ways:
1. As **environment variables**.
2. As **files** mounted into the container.

## Secrets are encoded, not encrypted
We stored the password `hunter2` (a throwaway for the demo) in a Secret. Reading it back gave `aHVudGVyMg==`. That is base64, which is just a way of writing bytes as text. One command turns it back into `hunter2`.

So a Secret does not hide anything from someone who can read it. What helps is limiting who can read it, and keeping it out of Git.

In this project the Secret was created from the command line, and its file is not in the repo. The ConfigMap, which has nothing sensitive, is in Git (`manifests/phase1/config-demo.yaml`). The real model API key will be handled like the Secret.

## Env var vs. file: when do changes show up?
We changed the ConfigMap while the pod was running:
- The **environment variable** did not change. Env vars are fixed when the container starts.
- The **mounted file** updated by itself, after about 80 seconds. The kubelet refreshes mounted ConfigMaps on a timer.
- A **new pod** saw the new value in both.

So if your app reads config from an env var, changing the ConfigMap needs a pod restart to take effect.

## Something we tripped over
Re-applying the full manifest file reset the ConfigMap back to what Git says, wiping our manual change. That is `kubectl apply` doing its job: make the cluster match the file.

At the end, the cluster's ConfigMap said `CHANGED value`, but Git said `hello from the ConfigMap`. That gap is called **drift**. Fixing drift automatically is what Argo CD does in Phase 2.

## Remember
- ConfigMap: settings. Secret: sensitive values. Both can come in as env vars or files.
- Base64 is not encryption.
- Env vars are fixed at start. Mounted files refresh over time.
- Never put real secrets in Git.
