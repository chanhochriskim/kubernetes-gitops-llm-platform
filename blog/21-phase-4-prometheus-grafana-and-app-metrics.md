# Phase 4: Prometheus, Grafana, and app metrics

## The idea
In Phase 3 we read cgroup files by hand, one moment at a time. Prometheus keeps those numbers over time, so you can see a trend, a spike or a gap. Phase 4 is Phase 3 with a time axis.

## What we installed (small on purpose)
Using Helm only to render YAML, which we saved in the repo (`manifests/phase4/monitoring/`) instead of running `helm install`:
- **Prometheus** (chart 29.47.2, app v3.16.0): scrapes and stores the numbers. 6 hours of retention, no disk volume.
- **kube-state-metrics** (v2.20.0): turns Kubernetes objects (restarts, pod status, HPA state) into metrics.
- **Grafana** (chart 10.5.15, app 12.3.1): draws graphs. The admin password is in a Secret created from the command line and is not in Git.

Left out to save memory on an 8 GB laptop: Alertmanager, node-exporter, pushgateway, the operator, and persistent storage.

Caveat: the `grafana/grafana` Helm chart is marked deprecated by its publisher. It still works and the Grafana version it installs is current, but a maintained chart is the better long-term choice.

## Pull, not push
Prometheus asks each target for its numbers every 30 seconds. If a target stops answering, the metric `up` becomes 0, so a crash is visible. With push, a crashed app just goes quiet, and silence looks the same as "nothing to report."

## What Prometheus scrapes
- `kubernetes-nodes-cadvisor` (3 targets): cAdvisor, built into each kubelet. It reads the same cgroup files we read by hand and exposes them as metrics, for example `container_cpu_cfs_throttled_periods_total` and `container_memory_working_set_bytes`.
- `kubernetes-nodes`, `kubernetes-api-servers`, `kubernetes-service-endpoints`, and Prometheus itself.
All 12 targets were up.

## Reading the throttling graph
We restarted the CPU hog from Phase 3. `rate(container_cpu_cfs_throttled_periods_total{pod="cpu-hog"}[1m])` sat at about 10.
- The kernel hands out CPU in 100 ms windows. The limit allows 10 ms per window.
- The hog always wants more, so it is throttled in every window. A second has 10 windows, so the rate is 10 per second. That is the maximum.
- It matches Phase 3: 100 throttled periods over 10 seconds.
- A flat line at the maximum means "this container is throttled all the time." It tells you a limit is too low without anything crashing.

Two lines appeared for one pod: one series for the container and one for the pod-level cgroup that contains it. It is the same data twice.

There was also a gap of about 3 to 4 minutes in the data (33 samples in 20 minutes where about 40 were expected). We did not find the cause. The VM or the Mac pausing is a guess and is not confirmed. The dips below 10 are also unexplained.

## What the kernel cannot tell you
cAdvisor sees CPU, memory and network, because the kernel knows those. It cannot see "did this request succeed?" Only the app knows that. So a graph of HTTP errors needs the app to publish its own metrics.

## Instrumenting the backend
We added `prometheus-client` to `backend/main.py`:
- A counter `http_requests_total` labeled by method, route and status code.
- A histogram `http_request_duration_seconds`, labeled by method and route.
- A `GET /metrics` page that Prometheus scrapes, and a `GET /fail` route that always returns 500, only for testing.
- The route label uses the route template (`/chat`), not the raw URL, to keep the number of label combinations small. Too many label values (high cardinality) is a classic way to overload Prometheus.

The Deployment got three annotations (`prometheus.io/scrape`, `port`, `path`) which tell Prometheus to scrape the pods. The image went from `chat-backend:0.1` to `0.2`.

Order matters. We loaded the new image into the Kind nodes before pushing, because Argo CD cannot see local images. A push first would have left the rollout stuck on `ImagePullBackOff`. A real cluster pulls from a registry, which removes this manual step.

## What we saw
We sent 20 good chats, 5 requests to `/fail`, and 3 malformed chats. Prometheus counted exactly 20 with status 200, 5 with status 500, and 3 with status 422. The error rate (5xx over all requests, excluding the `/health` probes) was 17.9%, which is 5 of 28.

Two details:
- The 422s are client errors (4xx), so they are not part of a server error rate.
- Kubernetes calls `/health` every few seconds, so it dominates the counts unless you exclude it.

Our first reading was wrong: it showed 5, 2 and 4. I stopped waiting too early, when the total (inflated by health probes) passed a threshold, and read a partial snapshot taken before the last scrape. Waiting for the right condition gave the exact counts. With a 30 second scrape interval, a number you read right after an event can be behind.

## Remember
- Prometheus pulls, and a missing target is visible as `up = 0`.
- cAdvisor shows what the kernel knows. Application behavior, like error rates, needs app metrics.
- Flat at the maximum throttle rate means the CPU limit is too low.
- Counters only go up. Use `rate()` to turn them into a per-second value.
- Keep label values few.
