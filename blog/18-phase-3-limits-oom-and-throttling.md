# Phase 3, lesson 1: Limits, the OOM killer, and throttling

## The idea
A resource limit in YAML becomes a number in a cgroup file. The kernel enforces it. The two resources fail in different ways:
- **Memory over the limit:** the process is killed.
- **CPU over the limit:** the process is slowed down.

Requests and limits do different jobs:
- A **request** is what the scheduler uses to choose a node.
- A **limit** is what the kernel enforces.

## Memory: `mem-hog`
`manifests/phase3/mem-hog.yaml` runs `tail /dev/zero`. It never sees a newline, so it keeps buffering and grows without end. Limit: 64 Mi.

What we saw:
- Status `OOMKilled`, exit code **137** (128 plus signal 9, the kill signal).
- The kubelet restarted it each time, so `RESTARTS` climbed (2 after about 30 seconds) and the delay between restarts grows (the status moves to `CrashLoopBackOff`).
- On the node, in the pod's cgroup, `memory.events` showed:
  - `max 90`: the container hit its limit 90 times.
  - `oom 3`: three OOM events, one per run (the first start plus 2 restarts).
  - `oom_kill 6`: six processes killed, probably two per run (`sh` and `tail`).
  - `memory.max` was `67108864`, the 64 Mi limit.

Why kill? Memory is something a process holds. It cannot be taken back without destroying the data in it, so the only way to stay under the limit is to end the process.

## CPU: `cpu-hog`
`manifests/phase3/cpu-hog.yaml` runs an endless loop that wants 100% of a CPU. Limit: 100m, which is 0.1 CPU. The cgroup file said `cpu.max = 10000 100000`: 10 ms of CPU time every 100 ms.

Over 10 seconds, from the cgroup's `cpu.stat`:
- CPU time used: about 1001 ms out of 10,000 ms, which is 10% of a CPU, exactly the limit.
- Times throttled: 100, once per 100 ms window.
- Time spent paused: about 8,989 ms.
- The pod stayed `Running` with 0 restarts.

Why throttle? CPU time is something you use up and get more of later. Pausing the process is safe, because nothing it holds is taken away.

## A picture
CPU is a tap: too much, and the flow is turned down. Memory is a bucket: too much, and it overflows and something has to go.

## Why this matters
- A service can be slow without ever crashing, because of CPU throttling. Latency goes up and nothing is restarted, so it is easy to miss.
- A service that leaks memory crashes in a loop. `CrashLoopBackOff` with exit code 137 is the sign.
- Setting a limit too low causes both problems on a healthy app. Setting no limit lets one pod take memory from the others on the node.

## Remember
- Memory limit exceeded: OOM kill, exit 137, restart.
- CPU limit exceeded: throttling, same pod keeps running.
- The kernel's cgroup files (`memory.events`, `cpu.stat`) are the ground truth.
- Requests are for scheduling. Limits are for enforcement.
