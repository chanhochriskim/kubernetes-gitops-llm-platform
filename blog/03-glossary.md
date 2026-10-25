# Glossary

**API server**: The front desk of Kubernetes. Every command and every component goes through it.

**cgroup (control group)**: A Linux feature that limits how much CPU, memory, and so on a group of processes can use.

**Cluster**: A group of computers (nodes) managed together by Kubernetes.

**Colima**: A tool that runs a small Linux machine on your Mac so Docker can work.

**Container**: A normal Linux process with a limited view (namespaces) and limited resources (cgroups).

**containerd**: The program on each node that actually creates and starts containers.

**Control plane**: The nodes that run the brain of the cluster (API server, etcd, scheduler, controller manager).

**Controller**: A loop that compares "what we want" to "what exists" and fixes the difference.

**CoreDNS**: Gives names to things inside the cluster so they can find each other.

**Docker**: A tool for building and running containers.

**etcd**: The database where Kubernetes stores everything it knows.

**Kind**: "Kubernetes in Docker". Builds a practice cluster where each node is a Docker container.

**kubectl**: The command-line tool you use to talk to Kubernetes.

**kubelet**: The manager running on each node. It makes sure the pods assigned to its node are running.

**Manifest**: A YAML file that describes something you want (a pod, a service, and so on).

**Namespace (Linux)**: A Linux feature that gives a process its own private view of something (PIDs, network, hostname, files). Not the same as a Kubernetes namespace, which is a way to group objects in a cluster.

**Node**: One computer in the cluster.

**OOM killer**: The part of the Linux kernel that kills a process when memory runs out.

**Pod**: The smallest thing Kubernetes runs. Usually one container.

**QoS class**: How Kubernetes ranks a pod for eviction. Guaranteed, Burstable, or BestEffort.

**Reconcile loop**: Another name for a controller loop: look, compare, fix, repeat.

**Request (resource)**: How much CPU or memory a pod asks for. The scheduler uses it to pick a node.

**Limit (resource)**: The most CPU or memory a pod may use. The kernel enforces it.

**Scheduler**: Picks which node a new pod runs on.

**Service**: A stable address in front of pods that come and go.

**Taint**: A "keep out" sign on a node. Pods stay away unless they tolerate it.

**Throttling**: Slowing a process down because it used up its CPU allowance.

**Worker node**: A node that runs your apps.
