# Phase 1, step 7: The backend, images, and loading them into Kind

## What we built
A small FastAPI backend (`backend/main.py`) with two routes:
- `GET /health`: returns `{"status":"ok"}`. The readiness and liveness probes use it.
- `POST /chat`: takes a question and returns an answer, plus the name of the pod that served it.

It runs in **fake mode** by default (the answer repeats your question), so no API key or cost is needed. API calls to a model are billed separately from a Claude subscription, so we chose not to use a real key for now. The code has one function, `call_real_model()`, where the real call goes later. Switching modes is a setting (`MODEL_MODE`) in a ConfigMap, and the key would come from a Secret named `llm-api-key`, marked `optional: true` so fake mode runs without it.

## Images and containers
- A **Dockerfile** is the recipe for an image: start from `python:3.12-slim`, install FastAPI, copy in the app, run it.
- An **image** is a packaged app. A **container** is a running copy of it.

## The image is not in the cluster
We built the image on the Mac (`docker build`, 271 MB). Then we applied a Deployment that used it, without loading it into the cluster. Result:
- Pods: `ImagePullBackOff`.
- Event: `Failed to pull image "chat-backend:0.1" ... docker.io/library/chat-backend:0.1 ... pull access denied`.

The nodes are separate containers with their own storage. They cannot see images on the Mac. Since the image was not on the node, the kubelet tried Docker Hub, which has no such image.

Fix: `kind load docker-image chat-backend:0.1 --name k8s-os`. It copied the image into all three nodes. We then deleted the pods, and the Deployment recreated them. They started.

`imagePullPolicy: IfNotPresent` in the manifest tells the kubelet to use the image already on the node. Real clusters pull from a registry (like Docker Hub or ECR). Loading by hand is the local-cluster shortcut for that.

## Calling it through the Service
From a throwaway pod, `http://backend/chat` worked by name. Both pods answered requests. The spread is not strict alternation. kube-proxy's default mode picks a backend at random for each new connection.

## Remember
- Image on the Mac is not the same as image in the cluster.
- `ImagePullBackOff` often just means the node cannot find the image.
- A ConfigMap sets the mode. A Secret (optional here) would hold the key.
- A Service spreads requests across the pods behind it.
