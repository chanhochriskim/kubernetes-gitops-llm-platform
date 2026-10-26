# Phase 0 review session

After finishing Phase 0, we ran a short question-and-answer review. This note records the questions, the answers, and where the first guesses went off. Wrong guesses are the useful part.

## Q1. A pod crashes, and a new one appears without any command. Why?
**Answer:** Kubernetes is a loop. It compares what you want to what exists, and fixes the gap.

**Your answer:** "The number of pods stays consistent. If one dies, a fresh one replaces it." Correct.

**Detail to remember:** there are two "keep it running" loops.
- Inside one pod, the kubelet restarts a crashed or finished *process*. The pod stays.
- Across many pods, a **Deployment** holds the "I want 3" number and replaces missing pods. That comes in Phase 1.
- A bare pod that you delete does not come back.

## Q2. Which two components act after `kubectl apply`, and what is each one's job?
**Answer:**
- The **scheduler** picks which node the pod goes on.
- The **kubelet** on that node gets it started, by asking **containerd** to create the container.

**First guess:** cgroups and namespaces. Not quite. Those are the *tools* containerd and the kernel use after the kubelet gives the job.

**Picture:** a restaurant. The scheduler is the host who assigns the table. The kubelet is the waiter. containerd is the kitchen.

## Q3. How does the kubelet find out a pod was assigned to it?
**Answer:** through the API server. The scheduler writes the node name onto the pod. Every kubelet *watches* the API server and notices.

The scheduler and kubelet never talk directly. They only read and write at the front desk. That is why parts can crash and restart without breaking each other.

**Your answer:** correct.

## Q4. The `sleep` process was PID 1 inside the pod and PID 14814 on the node. One process or two?
**Answer:** one process. The **PID namespace** gives the container its own numbering.

**Picture:** two phone books. Outside, the person is "extension 14814". Inside, the same person is "extension 1". The container only has the inside book, so it cannot see other processes on the node. The node has the outside book and can see everything.

**Your answer:** correct. "Depending on where you are, the visibility differs."

## Q5. What happens when a process goes over its CPU limit, versus its memory limit?
**First guess:** "they reset." That is half right.

**Answer:**
- **Memory:** the kernel kills the process (the **OOM killer**). The kubelet restarts it. The status shows `OOMKilled`, exit code 137. Memory is something the process *holds*, and it cannot be taken back without destroying the data.
- **CPU:** the process is **throttled**, meaning paused until the next time window. Nothing is lost.

**Picture:** CPU is a tap, so you turn it down. Memory is a bucket, so it overflows and something has to go.

In the cgroup files: `cpu.max = 10000 100000` means 10 ms of CPU every 100 ms.

## Q6. Say it back: what happens in each case?
**Your answer:** CPU is throttled, which is safe. Memory hits the OOM killer, gets killed, and restarts. Correct.

**Two small fixes:**
- Throttling pauses the process until the next window. It does not stop it for good.
- After a restart the memory *limit* is the same (64 Mi). The memory *usage* starts again from zero. A leaky program would hit the limit again.

## Score
5 out of 6 on the first or second try. The one missed was the scheduler versus the kubelet.

## The five things to remember
1. Kubernetes is a loop: want versus have, fixed continually.
2. The scheduler picks the node. The kubelet and containerd start the process.
3. Components talk through the API server, never directly.
4. A container is a process. One process has different PIDs depending on who is looking.
5. CPU over the limit means slowed down. Memory over the limit means killed and restarted.

## Next
Phase 1: deploy the real app. First idea: the Deployment, which holds the "I want 3 pods" number.
