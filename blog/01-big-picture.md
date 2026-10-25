# The big picture

## What is this project?
We run a small app on Kubernetes on a laptop. While we do it, we learn what Kubernetes is really doing underneath.

## What is Kubernetes?
Kubernetes is a program that runs your other programs for you. You tell it what you want, for example "keep 3 copies of my app running". Kubernetes then makes that true, and keeps it true. If a copy crashes, it starts a new one.

## The one idea to remember
Kubernetes is a loop:

1. You write down what you **want** (the desired state).
2. Kubernetes looks at what **exists** right now.
3. If they are different, it fixes the difference.
4. It repeats this forever.

Almost everything in this project is this loop in a new place.

## Why the "operating system" angle?
You already know operating systems. Your shell project used `fork()` and `exec()` to start processes. Kubernetes does the same job, but across many computers instead of one:

| On one computer (OS) | On many computers (Kubernetes) |
|---|---|
| A process | A container |
| The CPU scheduler picks which process runs | The scheduler picks which computer runs a pod |
| Memory limits and the OOM killer | The same, set in YAML |
| Pipes and sockets between processes | Services and pod networking |

So if you understand the left column, the right column is not new. It is the same idea, bigger.

## The four phases
- **Phase 0:** Look inside a cluster. See that a container is just a process. (done)
- **Phase 1:** Deploy the real app, and reach it over HTTPS.
- **Phase 2:** Let Git control the cluster (GitOps).
- **Phase 3:** Set CPU and memory limits, break them on purpose, and make the app scale.
- **Phase 4:** Add dashboards so we can see everything.
