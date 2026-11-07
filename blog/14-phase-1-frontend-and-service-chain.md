# Phase 1, step 8: The frontend and a chain of Services

## What we built
A tiny frontend: one HTML page (`frontend/index.html`) served by nginx, in its own image (`web-frontend:0.1`, 76 MB). We used a static page instead of Next.js to save disk and time on an 8 GB laptop. It teaches the same Kubernetes ideas, and Next.js can replace it later.

## The browser problem
The page's JavaScript runs in your browser, on your Mac. Your browser does not know what `backend` means, because that name only works inside the cluster. So the page cannot call the backend directly.

The fix: the page calls `/api/chat` on its own server. The nginx pod then forwards `/api/` to `http://backend/`, which works because nginx is inside the cluster and can use cluster DNS. The nginx config line is `proxy_pass http://backend/;`.

This pattern is called a **reverse proxy**: a server that takes requests and passes them on to another server.

## The path of a request
client -> frontend Service -> one nginx pod -> backend Service -> one backend pod

Each Service picks a pod on its own.

## What we saw
We sent 12 requests to `http://frontend/api/chat` from a test pod:
- Backend pods answered 5 and 7 requests.
- Frontend (nginx) pods handled 8 and 4 requests.

Each layer spread the requests across its two pods, unevenly. That is the random choice kube-proxy makes for each new connection, not strict alternation. We did not track which frontend pod paired with which backend pod.

## Gotcha to remember
nginx looks up `backend` when it starts. If the backend Service does not exist yet, nginx can fail to start. In our case the Service existed first.

## Remember
- Browser code runs on your machine, not in the cluster.
- A reverse proxy lets the cluster hide its internal names behind one entry point.
- Services chain: each one balances over its own pods.
- Nothing here is reachable from your browser yet. That is the job of ingress, the next step.
