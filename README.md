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
- App: Next.js frontend, FastAPI backend, PostgreSQL
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

**Phase 1: Declarative app and ingress** (in progress)
- [x] Deployments, ReplicaSets and Services
- [x] Readiness and liveness probes (readiness tested by breaking a pod)
- [x] Rolling update, a deliberately broken update, and rollback
- [x] ConfigMaps and Secrets
- [x] PostgreSQL as a StatefulSet with a persistent volume
- [ ] FastAPI backend with a chat endpoint calling a hosted model
- [ ] Next.js frontend
- [ ] Ingress-NGINX with a local hostname
- [ ] HTTPS with cert-manager

**Phase 2: GitOps** (not started)
- Install Argo CD and point it at this repo
- Git is the source of truth; `kubectl` is for inspection only
- Change things by hand and watch Argo CD revert the drift

**Phase 3: Resources and scaling** (not started)
- Requests and limits, and how they become cgroup settings
- Trigger an OOMKill on purpose, read the exit code, then tune
- HPA on CPU with a Locust load test, observing scale-out and scale-in

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
