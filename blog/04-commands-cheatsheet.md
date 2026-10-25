# Commands cheat sheet

## Start and stop the machine
- `colima start --cpu 4 --memory 5 --disk 30`: start the Linux machine.
- `colima stop`: stop it. This frees the memory and CPU.
- `colima delete`: remove it completely. This frees all its disk space.

## Make and remove the cluster
- `kind create cluster --config cluster/kind-config.yaml`: build the cluster.
- `kind delete cluster --name k8s-os`: remove it.

## Look at the cluster
- `docker ps`: the node containers.
- `kubectl get nodes`: the nodes, as Kubernetes sees them.
- `kubectl get pods -n kube-system`: the system pods.
- `kubectl get pod NAME -o wide`: one pod, plus which node it is on.
- `kubectl describe pod NAME`: details, with events at the bottom.

## Create things from a file
- `kubectl apply -f FILE.yaml`: create or update what the file describes.
- `kubectl delete -f FILE.yaml`: remove it.

## Go inside
- `kubectl exec POD -- ps`: run `ps` inside a pod.
- `docker exec NODE sh -c '...'`: run a command inside a node.

## Look at containers as processes (run inside a node)
- `ps -eo pid,ppid,args`: list processes.
- `ls -l /proc/PID/ns`: the namespaces of a process.
- `cat /proc/PID/cgroup`: the cgroup of a process.
- `cat /sys/fs/cgroup/<path>/memory.max`: the memory limit.
- `cat /sys/fs/cgroup/<path>/cpu.max`: the CPU limit.

## Clean up the Mac
- `docker system prune -af --volumes`: remove unused Docker data.
- `docker builder prune -af`: remove build cache.
- `brew cleanup --prune=all`: remove Homebrew caches.
- `df -h /System/Volumes/Data`: check free disk space.
