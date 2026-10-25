# Phase 0: Cluster anatomy

## Cluster shape
`cluster/kind-config.yaml` creates 3 Kind nodes (1 control-plane, 2 workers). `docker ps` shows 3 containers; `kubectl get nodes` shows the same 3 machines. Each Kubernetes node is a container running its own kubelet and containerd. From macOS, none of the Kubernetes processes are visible, because they live inside the node containers inside the Colima VM.

Kind publishes the API server (6443) on a random localhost port, and our config forwards host ports 80 and 443 to the control-plane node for the ingress controller in Phase 1.

## What runs in kube-system
| Pod | Role |
|---|---|
| etcd | key-value store holding all cluster state |
| kube-apiserver | the only component that reads or writes etcd; every other component and kubectl talks to it |
| kube-scheduler | assigns unscheduled pods to nodes |
| kube-controller-manager | runs the reconcile loops (Deployments, ReplicaSets, nodes, ...) |
| kube-proxy (per node) | implements Service virtual IPs |
| kindnet (per node) | pod networking between nodes |
| coredns (x2) | cluster DNS |

The control plane itself runs as static pods that the kubelet starts from manifest files on the node.

## Scheduling a pod
`manifests/phase0/test-pod.yaml` is a busybox pod running `sleep 3600`. Events, in order:
1. `Scheduled` (default-scheduler): wrote the chosen `nodeName` into the pod object.
2. `Pulling`, `Pulled` (kubelet): the kubelet on that node noticed a pod assigned to it and had containerd fetch the image.
3. `Created`, `Started` (kubelet): containerd started the process.

The scheduler never contacts the node. It only sets a field through the API server; the kubelet finds out by watching. The pod landed on a worker because the control-plane has the taint `node-role.kubernetes.io/control-plane:NoSchedule`. Scheduling is filter (remove nodes that cannot run the pod) then score (rank the rest), not round robin.

## A container is a process
The same process has two identities:
- Inside the pod: `sleep 3600` is PID 1.
- On the node: the same process is PID 14814, with parent `containerd-shim-runc-v2`.
`/proc/<pid>/status` shows `NSpid: 14814 1`: the PID at each namespace level, outer first.

Namespaces (`/proc/<pid>/ns`) differ from the node's for cgroup, ipc, mnt, net, pid and uts, so the process sees its own PIDs, network, hostname, mounts and IPC. `user` and `time` namespaces are shared with the node. Namespaces control what a process can see.

Cgroup (`/proc/<pid>/cgroup`):
`/kubelet.slice/kubelet-kubepods.slice/kubelet-kubepods-besteffort.slice/kubelet-kubepods-besteffort-pod<uid>.slice/cri-containerd-<id>.scope`
The path encodes the pod's QoS class (`besteffort`, because we set no requests or limits). Cgroups control what a process can use. In Phase 3 the limits we set will appear as files in this directory.

## The pod restarted 20 times in a day
`sleep 3600` exits with code 0 after one hour. The default `restartPolicy: Always` makes the kubelet start it again every time. Kubernetes keeps a pod running even when the process finishes cleanly. This is the same idea as a reconcile loop: desired state is "running", so a finished process is a difference to fix.
