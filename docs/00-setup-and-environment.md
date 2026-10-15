# Setup and environment

## Why Colima instead of Docker Desktop
Kind runs Kubernetes nodes as Docker containers, so a container engine is required. On macOS, containers need a Linux kernel, which means a Linux VM sits underneath regardless of which tool is used. Colima runs that VM with a fixed CPU, memory, and disk ceiling, and `colima delete` returns all of the disk. Docker Desktop's VM disk grows and is harder to shrink, which was a problem on this machine earlier.

## Layers on this machine
macOS -> Colima Linux VM (Virtualization.Framework) -> Docker engine -> Kind node containers -> containerd -> application containers

Namespaces and cgroups only exist inside the Linux VM, not on macOS. Every "container is a process" experiment later happens inside it.

## Install
    brew install colima docker kind kubectl helm
    colima start --cpu 4 --memory 5 --disk 30

Versions: Docker 29.5.2, kind 0.33.0, kubectl 1.37.1, helm 4.3.0.

## Resource budget
Machine: 8 GB RAM, 8 cores, Apple Silicon. VM capped at 4 CPUs, 5 GB RAM, 30 GB disk (a ceiling; the disk fills on demand).
Free disk on the Mac: 29 GB before install, 23 GB after.

## End-of-session cleanup
    kind delete cluster --name k8s-os
    docker system prune -af --volumes
    docker builder prune -af
    colima stop
    brew cleanup --prune=all
The cluster is rebuilt from files in Git, so deleting it loses nothing.
