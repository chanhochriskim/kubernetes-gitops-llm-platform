# Phase 1, step 1: Deployments

## The idea
A **Deployment** is the "I want 3 pods" loop from Phase 0, made real. You write the number you want. Kubernetes keeps that many running.

## The three layers
Deployment -> ReplicaSet -> Pods

- The **Deployment** holds the plan: which image, how many copies, how to update.
- The **ReplicaSet** is the one that actually counts pods and creates or removes them to match the number.
- The **Pods** run the containers.

You do not create pods by hand. You change the Deployment, and the layers below follow.

## What we ran
`manifests/phase1/hello-deployment.yaml`: 3 replicas of a small nginx web server (a stand-in until the real app).

Key lines:
- `replicas: 3` is the number we want.
- `template` is the blueprint used for every pod.
- `labels` on the pod and `selector` on the Deployment are how the Deployment finds its own pods. They must match.

## What we saw
- 3 pods started in about 4 seconds.
- They landed on the two worker nodes (2 on one, 1 on the other). None went on the control-plane, because of its taint.
- We deleted one pod by hand. A new one was running within 1 second, and the ReplicaSet's event log says `Created pod`. Nobody typed a command.

## Who fixed it
The ReplicaSet controller (part of the controller manager) saw "want 3, have 2" and created one more. Then the scheduler placed it, and the kubelet started it. Same chain as Phase 0, with a loop at the start.

## Remember
- A Deployment keeps a count. A bare pod does not.
- Pods are disposable. The new pod has a different name and a different IP. That is a problem for anything trying to reach the pods, and it is the reason Services exist (next step).
