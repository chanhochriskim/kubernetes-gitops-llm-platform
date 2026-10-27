# kubernetes-gitops-llm-platform

A learning project: run a small three-tier app (Next.js, FastAPI, PostgreSQL) on a local multi-node Kubernetes cluster, and treat Kubernetes as a distributed operating system. Each step maps a cluster concept back to the OS concept underneath it (processes, cgroups, namespaces, the scheduler, the OOM killer).

## Stack

- Cluster: Kind (multi-node, on Docker)
- App: Next.js frontend, FastAPI backend, PostgreSQL
- Ingress and TLS: Ingress-NGINX, cert-manager (self-signed)
- GitOps: Argo CD
- Scaling: metrics-server, Horizontal Pod Autoscaler
- Observability: Prometheus, Grafana

## Roadmap

**Phase 0: Cluster anatomy**
- Create a multi-node Kind cluster from a config file.
- Trace one pod end to end: API server, etcd, scheduler, kubelet, container runtime.
- Find a container's process, namespaces and cgroup on the node.

**Phase 1: Declarative app and ingress**
- Write plain manifests: Deployments, Services, ConfigMaps, Secrets.
- Postgres as a StatefulSet with a persistent volume.
- Liveness and readiness probes, rolling updates.
- Ingress-NGINX with a local hostname, HTTPS via cert-manager.

**Phase 2: GitOps**
- Install Argo CD and point it at this repo.
- Git is the source of truth; `kubectl` is for inspection only.
- Break things by hand and watch Argo CD revert the drift.

**Phase 3: Resources and scaling**
- Set CPU/memory requests and limits and see them become cgroup settings.
- Trigger an OOMKill on purpose, read the exit code and kernel behavior, then tune.
- HPA on CPU, load test with Locust, observe scale-out and scale-in.

**Phase 4: Observability**
- Prometheus and Grafana via Helm.
- Dashboards for CPU throttling, memory saturation, restarts, HTTP error rate.

## Layout

- `cluster/`: Kind cluster config
- `manifests/`: Kubernetes manifests, grouped by phase
- `blog/`: beginner-friendly notes, read in order
- `docs/`: notes on what was set up and learned, one file per step

More directories are added as each phase lands.

## Status

Phase 0 complete. Phase 1 in progress: Deployment, Service, probes and rolling updates done on a stand-in `hello` app. Remaining: ConfigMaps and Secrets, Postgres on a StatefulSet, the FastAPI backend calling a model, ingress and HTTPS. See `blog/` for beginner notes and `docs/` for technical write-ups.
