# Phase 1, step 9: Ingress

## The problem
Services only work inside the cluster. Nothing on your Mac could reach the app. We need a front door that takes outside requests and sends them to the right Service.

## The pieces
- **Ingress controller:** a pod running nginx that listens on ports 80 and 443. It is the front door. We used Ingress-NGINX v1.15.1.
- **Ingress rule:** a small object that says where to send what. Ours, in plain words: "if the request is for host `app.local`, send it to the `frontend` Service on port 80."
- **Service:** still picks the pod. Ingress sends traffic to a Service, not directly to a pod.

The controller watches Ingress objects and rewrites its own nginx config to match. That is another reconcile loop.

## How the request gets from the Mac to the cluster
Back in Phase 0 our Kind config forwarded Mac ports 80 and 443 to the control-plane node. The controller pod uses `hostPort` 80 and 443, so it listens on exactly those ports on that node.

Path of one request:
Mac port 80 -> control-plane node -> ingress controller -> frontend Service -> nginx pod -> backend Service -> backend pod

## Something we caught
The upstream manifest for this version only requires `kubernetes.io/os: linux`. It does not require our `ingress-ready` label (older versions did). The scheduler could have placed the controller on a worker node, where our port mapping does not exist, and the app would be unreachable from the Mac.

The fix: a small kustomize patch (`manifests/phase1/ingress-nginx/kustomization.yaml`) that adds `nodeSelector: ingress-ready: "true"`. We kept the downloaded upstream file (`deploy.yaml`) unchanged and put our change in the patch, so it is easy to see what we changed. We verified the pod landed on `k8s-os-control-plane`.

Note that the Ingress-NGINX project has been retired upstream. It still works and is fine for learning. Gateway API is the newer approach.

## What we saw
Using curl with the Host header set by hand:
- `Host: app.local` returned the page.
- A POST to `/api/chat` returned the fake model's answer.
- `Host: other.local` returned `404`, because no rule matches it.

## Why a hostname?
Ingress matches on the host name in the request. Your browser has to send `Host: app.local`, which means your Mac has to know that `app.local` means your own machine. That is done with a line in `/etc/hosts`:
127.0.0.1 app.local

## Remember
- Ingress controller = the door. Ingress rule = the directions.
- Ingress routes to Services, and Services pick pods.
- Check which node a controller lands on when you depend on a host port.
- No matching rule means 404.
