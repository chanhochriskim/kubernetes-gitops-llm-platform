# How to review Phase 0

Reading alone is not enough. You remember more when you try to answer from memory first. So this guide has three parts: read, quiz yourself, and explain it out loud.

## Part 1: Read (about 25 minutes)

Read the files in this order. Do not skip ahead.

1. `01-big-picture.md` (5 min). Goal: say the "want vs. have" loop in your own words.
2. `02-phase-0-walkthrough.md` (15 min). Read one step at a time. After each step, close your eyes and say what happened.
3. `03-glossary.md` (5 min). Do not memorize it. Just skim, and come back when a word is unfamiliar.

Skip `04-commands-cheatsheet.md` for now. It is for later, when you run things yourself.

Tip: read it on GitHub in your browser, or open the folder in any text editor.

## Part 2: Quiz yourself (about 15 minutes)

Cover the answers. Write or say your answer first. Then check.

**Q1. What is Kubernetes, in one sentence?**
A program that runs your other programs, and keeps them running the way you asked.

**Q2. What is the "loop" that Kubernetes runs?**
Look at what you want. Look at what exists. If they differ, fix it. Repeat forever.

**Q3. Our cluster has 3 nodes. What are they really?**
Three Docker containers. Each one pretends to be a computer.

**Q4. Why couldn't `ps` on your Mac see any Kubernetes process?**
They run inside a Linux machine (Colima) inside your Mac. macOS is not Linux, so it has no view into it.

**Q5. What does etcd do? What does the API server do?**
etcd stores everything Kubernetes knows. The API server is the front desk. Everyone talks to it, and only it talks to etcd.

**Q6. When you create a pod, who picks the node, and who starts the container?**
The scheduler picks the node. The kubelet on that node starts the container (with help from containerd).

**Q7. Does the scheduler talk to the node directly?**
No. It writes the node's name on the pod. The kubelet notices by watching the API server.

**Q8. Why did our pod not go on the control-plane node?**
That node has a taint, a "keep out" sign. Our pod did not say it accepts it.

**Q9. The `sleep` process had two PIDs: 1 and 14814. Why?**
It is one process. Inside the container it sees its own numbering, so it is PID 1. On the node, the real number is 14814. The PID namespace makes the difference.

**Q10. Namespaces vs. cgroups: what does each one control?**
Namespaces control what a process can see. Cgroups control how much it can use.

**Q11. What is `memory.max = 67108864`?**
The memory limit in bytes. 64 × 1024 × 1024 = 64 Mi, the limit we set in YAML.

**Q12. Do cgroup files take up disk space?**
No. They are virtual. The kernel makes them up when you read them.

**Q13. A process uses too much CPU. Another uses too much memory. What happens to each?**
Too much CPU: it gets slowed down (throttled). Too much memory: it gets killed by the OOM killer.

**Q14. Why did the pod restart 20 times?**
`sleep 3600` ended after an hour, and Kubernetes restarts pods by default. You want it running, it is not, so it fixes it.

Score yourself:
- 12 to 14 right: move on to Phase 1.
- 8 to 11 right: re-read the walkthrough steps for the ones you missed.
- Under 8: re-read `01-big-picture.md` and try again tomorrow. That is normal.

## Part 3: Explain it (about 10 minutes)

This is the best test. Pretend you are talking to a friend who knows nothing about this. Out loud, or on paper, explain these in 2 or 3 sentences each:

1. What is a container?
2. What happens when you create a pod?
3. How does a memory limit in YAML become a real limit?

If you get stuck, that is the part to re-read. Being stuck is useful. It shows you what to review.

## Part 4: Redo it yourself (optional, later)

When you have time and free disk space, rebuild the cluster and repeat the steps from `04-commands-cheatsheet.md`. Before each command, guess what it will print. Then run it and compare.

## A simple schedule
- Day 1: Part 1 and Part 2.
- Day 2: Part 2 again (only the ones you missed) and Part 3.
- Before Phase 1: one last pass over the big picture.
