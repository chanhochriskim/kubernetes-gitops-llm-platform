# Phase 1, step 3: Probes

## The problem
Kubernetes knows if a container's process is alive. It does not know if the app inside is working. A web server can be running and still be stuck, or still starting up.

## Probes: asking the app "are you okay?"
Two kinds, with two different jobs.

**Readiness probe: "can you take traffic?"**
- If it fails, the pod keeps running and is **not restarted**.
- The Service stops sending requests to it, until the probe passes again.

**Liveness probe: "are you stuck?"**
- If it fails, the kubelet **restarts** the container.

Rule of thumb: readiness controls traffic. Liveness controls restarts.

## What we added
In `manifests/phase1/hello-deployment.yaml`:
- Readiness: an HTTP request to `/index.html` every 2 seconds. Two failures in a row mean not ready.
- Liveness: just a check that port 80 accepts a connection, every 5 seconds.

## What we did
Changing the pod blueprint made Kubernetes replace the pods one by one (a rolling update, covered in step 5).

Then we broke one pod on purpose. We moved `index.html` out of the web server's folder inside one pod. Result:
- The probe got a 404, and the event log said `Readiness probe failed: HTTP probe failed with statuscode: 404`.
- The pod showed `READY false` and `RESTARTS 0`. It was not restarted.
- In the Service's endpoint list, the pod was still listed but marked `ready=false`. The Service skips those.
- When we moved the file back, the pod went back to `ready=true` on its own.

## A note on reading the output
Listing a Service's endpoints shows not-ready pods too. The `ready` flag is what matters. Looking at only the IP list can make you think a broken pod is still receiving traffic.

## Why this matters
- During a deploy, readiness stops traffic going to a pod that is still starting.
- A bad liveness probe can cause restart loops. If it is too strict, Kubernetes keeps killing a healthy but slow app. Keep liveness simple.

## Remember
- Readiness fail: pod stays, traffic stops.
- Liveness fail: container restarts.
- We tested readiness. We did not trigger a liveness failure.
