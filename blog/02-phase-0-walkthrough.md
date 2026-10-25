# Phase 0 walkthrough

Goal: understand what is actually inside a Kubernetes cluster, before we put an app on it.

## Step 1: Set up the tools
Kubernetes needs Linux. A Mac is not Linux. So we run a small Linux machine inside the Mac. A tool called **Colima** does that. Inside it runs **Docker**. A tool called **Kind** then uses Docker to build a cluster.

The layers, from the bottom up:

1. Your Mac
2. A small Linux machine (Colima)
3. Docker
4. Three "node" containers (Kind)
5. Your app's containers, running inside the nodes

Remember this: all the Linux features we look at later (namespaces, cgroups) live in layer 2. They do not exist on macOS.

We limited the Linux machine to 4 CPUs, 5 GB of memory, and 30 GB of disk. That keeps the project from eating your Mac.

## Step 2: Create a cluster with 3 nodes
A **node** is one computer in the cluster. Ours are fake computers: each one is a Docker container. We made:

- 1 **control-plane** node: the brain.
- 2 **worker** nodes: where apps run.

We saw the same three machines two ways. `docker ps` shows them as containers. `kubectl get nodes` shows them as Kubernetes nodes. Same thing, two views.

You also found out that `ps` on your Mac cannot see any Kubernetes process. They are all inside the Linux machine. Your guess "you have to go lower than macOS" was right.

## Step 3: Meet the brain
The control-plane node runs these pieces. Each one has one job:

- **etcd:** the notebook. It stores everything Kubernetes knows.
- **API server:** the front desk. Everyone talks to it. Only it touches etcd.
- **Scheduler:** the planner. It chooses which worker runs a new pod.
- **Controller manager:** the fixer. It runs the "want vs. have" loops.

On each node there are also:

- **kubelet:** the node's manager. It starts the containers it is told to start.
- **containerd:** the worker that really starts containers.
- **kube-proxy** and **kindnet:** networking.

And **CoreDNS** turns names into addresses inside the cluster.

## Step 4: Create one pod and watch
We made a pod that runs `sleep 3600`. The events showed what happened, in order:

1. **Scheduler** picked a node and wrote its name on the pod.
2. **Kubelet** on that node noticed.
3. **Kubelet** asked containerd to download the image.
4. **containerd** created and started the container.

The key point: the scheduler never talks to the node. It only writes a note. The kubelet reads the note. All parts talk through the API server, not to each other.

## Why didn't the pod go on the control-plane?
The control-plane has a **taint**. A taint is a "keep out" sign. Pods are refused unless they say they accept it. Our pod did not, so it went to a worker.

You guessed "round robin". The real process is: first remove the nodes that cannot run the pod, then score the rest and take the best.

## Step 5: A container is just a process
This is the main lesson of Phase 0.

We looked at the `sleep` process from two places:

- Inside the pod, it is **PID 1**.
- On the node, it is **PID 14814**.

It is the same process. Linux just shows it with a different number depending on who is looking.

What makes this work are two Linux features.

**Namespaces decide what a process can see.** The container got its own PID numbers, its own network, its own hostname, and its own files. It cannot see the other processes on the node.

**Cgroups decide how much a process can use.** They limit CPU and memory.

Short version:
- Namespaces = what you can **see**.
- Cgroups = what you can **use**.

A container is a normal Linux process with those two things attached.

## Step 6: Limits are just numbers in files
We made a pod with these limits: 64 Mi of memory and 0.1 CPU. Then we read the cgroup files on the node:

- `memory.max` was `67108864`. That is 64 × 1024 × 1024 bytes.
- `cpu.max` was `10000 100000`. That means 10 ms of CPU allowed every 100 ms, which is 0.1 CPU.

These files take no disk space. The kernel makes them up on the spot. Reading one asks the kernel a question. Writing one changes how the kernel behaves.

So when you write `memory: 64Mi` in YAML, Kubernetes ends up writing a number into a file.

## Step 7: The pod restarted 20 times
`sleep 3600` ends after an hour. Kubernetes then started it again, because the default rule is "always keep it running". This is the loop from the big picture: you want it running, it is not running, so fix it.

## What to remember
1. Kubernetes is a loop: want vs. have.
2. Components talk through the API server, not to each other.
3. A container is a process. Namespaces limit what it sees. Cgroups limit what it uses.
4. A limit in YAML is a number in a kernel file.
5. Going over a CPU limit slows you down. Going over a memory limit gets you killed. (We try this in Phase 3.)

## What we got wrong, and what we learned
- "docker ps will show 1": it shows 3, one per node.
- "round robin": no, the scheduler filters and scores.
- "the process will not show on the node": it does, with a different PID.
- "the files will use disk": no, they are virtual.

Wrong guesses are how this sticks. Keep guessing.
