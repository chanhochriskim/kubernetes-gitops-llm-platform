# Phase 3, lesson 2: QoS classes and setting limits through Git

## QoS: Kubernetes ranks pods by what you promised
You do not set the class. Kubernetes works it out from the requests and limits you wrote:
- **Guaranteed:** every container has requests equal to limits, for both CPU and memory.
- **Burstable:** some requests or limits are set, but they are not equal.
- **BestEffort:** nothing is set.

When a node is short on memory, BestEffort pods lose first, then Burstable, then Guaranteed.

## How the kernel gets involved
The kubelet writes a number into `/proc/<pid>/oom_score_adj` for each container process. The Linux OOM killer reads it. A higher number means killed sooner. We created one pod of each class (`manifests/phase3/qos-demo.yaml`) and read the kernel:
- BestEffort: `1000` (the maximum, killed first)
- Burstable: `994` (computed from the memory request relative to the node's memory)
- Guaranteed: `-997` (strongly protected)

Kubernetes does not choose the victim itself. It sets a score, and the kernel acts on it.

## A finding about our own apps
Every pod in the cluster was BestEffort, including the backend, the frontend and all of Argo CD. We had never set requests or limits. Those would have been the first to die under memory pressure.

## Setting limits through Git
We added `resources` to `deploy/app/backend.yaml` and `deploy/app/frontend.yaml`:
- Backend: requests 50m CPU and 64 Mi, limits 250m CPU and 128 Mi.
- Frontend: requests 10m CPU and 16 Mi, limits 100m CPU and 64 Mi.

Both are now Burstable. We committed and pushed. We told Argo CD to check Git right away (a refresh) instead of waiting for its poll. It synced, and the cluster showed `Synced` at the commit we pushed. No `kubectl apply` for the apps.

## The rollout
Changing the pod blueprint triggers a rolling update. The cluster's event log showed it in steps over about 19 seconds: one new pod up, one old pod down, repeat. The old ReplicaSets ended at 0 and the new ones at 2 and 3. All pods were never down at once.

## Kernel confirmation
In the cgroup files on the node:
- Backend: `memory.max = 134217728` (128 Mi), `cpu.max = 25000 100000` (0.25 CPU).
- Frontend: `memory.max = 67108864` (64 Mi), `cpu.max = 10000 100000` (0.1 CPU).

Actual use at the time: the backend about 32 MiB, the frontend about 4 MiB. The cgroup number includes file cache, so it reads a little above the app's own memory.

## Picking the numbers
These are first guesses based on the size of the apps. The backend request (64 Mi) is above its use (32 Mi), so it could be lower. A request that is too high wastes room on the node. A limit too low causes OOM kills. Real tuning needs measurement over time, which is what Phase 4 (Prometheus) is for.

## A reminder about the nodes
All three Kind nodes are containers sharing one VM, so each node reports the VM's full memory. The scheduler therefore sees about 3 times more memory than exists. A real cluster has separate machines.

## Remember
- QoS class comes from your requests and limits.
- The class sets `oom_score_adj`, and the kernel kills the highest score first.
- A limit set in Git reaches the kernel through Argo CD, the kubelet and the cgroup.
- Measure before tuning.
