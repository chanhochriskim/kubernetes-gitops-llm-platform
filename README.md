# kubernetes-gitops-llm-platform

A hands-on project to learn how Kubernetes actually works, by running a small three-tier app (Next.js, FastAPI, PostgreSQL) on a local multi-node cluster and treating Kubernetes as a distributed operating system.

Every step maps a cluster concept back to the operating-system idea underneath it: containers are processes, resource limits are cgroup settings, the scheduler is a cluster-wide CPU scheduler, and an out-of-memory kill is the kernel OOM killer. The goal is to understand the system, not just to get an app deployed.

## Who this is for and why it exists

I am a CS student (Purdue, class of 2027) with a background in systems programming (a Unix shell and a C compiler), backend services, and GenAI pipelines. I have used Kubernetes as a consumer, for example to pull storage credentials and thread dumps from clusters during an internship. This project fills the gap: how the cluster works inside, how to run services on it reliably, and how to see what it is doing.

The project is also a record of how I learn. I predict what will happen before running each step, then compare, and the notes keep the wrong guesses.

## Skills this project builds

| Area | What I practice here |
|---|---|
| Kubernetes fundamentals | Control plane components, the reconcile loop, scheduling, Deployments, Services, StatefulSets, probes, rolling updates and rollback |
| Linux and OS internals | Namespaces, cgroups v2, PID mapping between host and container, the OOM killer, CPU throttling |
| Config and secrets | ConfigMaps, Secrets, env vars vs mounted files, what base64 does and does not protect |
| State and storage | PersistentVolumes and claims, StatefulSets, how data survives pod replacement |
| Networking | Pod IPs, Services, cluster DNS, ingress, TLS certificates |
| GitOps and delivery | Git as the source of truth, Argo CD, drift detection and self-healing |
| Reliability and scaling | Requests and limits, autoscaling with HPA, load testing, failure testing |
| Observability | Prometheus metrics, Grafana dashboards, reading saturation and error signals |
| Working with AI models | A FastAPI service that calls a hosted model, API key handling, how model workloads behave under resource limits |
| Engineering habits | Small commits, documentation written as I go, testing claims by running them |

## Why these skills matter

Platform, SRE, DevOps and backend roles use the same few ideas: declarative configuration, automated delivery from Git, resource limits that match what the kernel enforces, and visibility into running systems. Being able to explain why a pod was OOM-killed, or why a rollout stalled, from the kernel up to the YAML is the kind of understanding that separates running `kubectl apply` from operating a cluster. That is the level I am working toward, and the repository shows each step with evidence rather than just the final config.

## Stack

- Cluster: Kind (3 nodes: 1 control plane, 2 workers), on Colima and Docker
- App: static nginx frontend (Next.js planned), FastAPI backend, PostgreSQL
- Ingress and TLS: Ingress-NGINX, cert-manager (self-signed)
- GitOps: Argo CD
- Scaling: metrics-server, Horizontal Pod Autoscaler
- Observability: Prometheus, Grafana

## Roadmap and status

**Phase 0: Cluster anatomy** (done)
- [x] Multi-node Kind cluster from a config file
- [x] Traced one pod end to end: API server, scheduler, kubelet, containerd
- [x] Found a container's process, namespaces and cgroup on the node
- [x] Read CPU and memory limits back from cgroup files

**Phase 1: Declarative app and ingress** (core done)
- [x] Deployments, ReplicaSets and Services
- [x] Readiness and liveness probes (readiness tested by breaking a pod)
- [x] Rolling update, a deliberately broken update, and rollback
- [x] ConfigMaps and Secrets
- [x] PostgreSQL as a StatefulSet with a persistent volume
- [x] FastAPI backend with a chat endpoint (fake model mode; real model call is a later swap)
- [x] Frontend: a static page served by nginx that proxies `/api/` to the backend (Next.js can replace it later)
- [x] Ingress-NGINX (v1.15.1, vendored with a kustomize patch) routing `app.local` to the frontend
- [x] HTTPS with cert-manager (self-signed CA; tested with curl, browser step skipped)
- [ ] Not done: a liveness-failure test, wiring the backend to Postgres, a real model call

**Phase 2: GitOps** (in progress)
- [x] Argo CD v3.6.1 installed (dex and notifications scaled to 0 to save memory)
- [x] An Application watching `deploy/app` on `main`; the app deployed with no `kubectl apply`
- [x] Drift tested: with self-heal off Argo CD only reports it; with self-heal on it reverts a manual scale in about 2 seconds and recreates a deleted Service in about 6 seconds
- [x] Changed the app by committing to Git (frontend replicas 2 to 3); Argo CD deployed it about 80 seconds after the push (Git is polled)
- [ ] Bring ingress and cert-manager under Argo CD

**Phase 3: Resources and scaling** (in progress)
- [x] Memory limit exceeded: OOMKilled, exit code 137, kernel counters read from `memory.events`
- [x] CPU limit exceeded: throttling, about 10% of a CPU at a 100m limit, read from `cpu.stat`
- [x] QoS classes: BestEffort, Burstable and Guaranteed map to `oom_score_adj` 1000, 994 and -997, read from `/proc`
- [x] metrics-server and an HPA on the backend (50% CPU target, 2 to 5 pods), tested with a simple in-cluster load generator (not Locust); scale-up took 1 to 2 minutes, scale-down was clearly slower (5 minute stabilization window)
- [x] Found and fixed a GitOps trap: Argo CD self-heal and the HPA fought over `replicas`; the HPA now owns it and the HPA lives in `deploy/app/`
- [x] Requests and limits on the backend and frontend set through Git; Argo CD rolled them out and the cgroup files matched

**Phase 4: Observability** (not started)
- Prometheus and Grafana via Helm
- Dashboards for CPU throttling, memory saturation, restarts and HTTP error rate

## Things I have verified by running them

- Each Kind node is a Docker container, and none of the Kubernetes processes are visible from macOS, because they live inside the Linux VM.
- A container's process has one PID on the node and PID 1 inside the pod. The namespaces differ for pid, net, mnt, uts, ipc and cgroup.
- A `64Mi` memory limit appears as `memory.max = 67108864`, and a `100m` CPU limit as `cpu.max = 10000 100000`.
- Deleting a pod owned by a Deployment is repaired within about a second. A bare pod is not.
- A readiness failure removes a pod from the Service without restarting it.
- An update to a nonexistent image stalls, while the old pods keep serving traffic.
- A Secret is only base64-encoded. Env vars from a ConfigMap do not change in a running pod, but mounted files do.
- Database rows survive deleting the Postgres pod, because the data is on a volume.

## Layout

- `cluster/`: Kind cluster config
- `manifests/`: Kubernetes manifests, grouped by phase
- `blog/`: plain-language notes for each step, read in order (start with `blog/README.md`)
- `docs/`: more technical notes on setup and cluster internals

## Running it

Requirements: macOS or Linux, Colima (or another Docker runtime), `kind`, `kubectl`, `helm`.

```
colima start --cpu 4 --memory 5 --disk 30
kind create cluster --config cluster/kind-config.yaml
kubectl apply -f manifests/phase1/hello-deployment.yaml
```

Secrets are never committed. Manifests that need one say so in a comment, and the Secret is created from the command line.

To free disk space afterward:

```
kind delete cluster --name k8s-os
docker system prune -af --volumes
colima delete --data
```

The project is sized for an 8 GB laptop: the VM is capped at 4 CPUs, 5 GB of RAM and 30 GB of disk, and the cluster is deleted at the end of each session. Everything is rebuilt from the files in this repo.
