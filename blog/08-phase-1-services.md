# Phase 1, step 2: Services

## The problem
Pods are disposable. When a pod is replaced, its name and its IP address change. If another program had saved the old IP, it would break.

## The fix: a Service
A **Service** is a stable address in front of a group of pods. It has two parts:
- A fixed IP, called the **ClusterIP**. It does not change when pods are replaced.
- A DNS name (here, `hello`). **CoreDNS** turns the name into the ClusterIP.

**kube-proxy**, which runs on every node, forwards each request from the ClusterIP to one of the pods behind it.

Picture: a company's main phone number. Staff and desk phones change. The main number stays. The receptionist forwards your call to whoever is free.

## How the Service finds its pods
By label, not by name or IP. In `manifests/phase1/hello-service.yaml`, the line `selector: app: hello` means "send traffic to pods with the sticker `app=hello`". When a new pod appears with that sticker, it joins automatically. When one disappears, it leaves.

The list of pod IPs behind a Service is called its **endpoints**.

## What we saw
- The Service got ClusterIP `10.96.19.21`.
- Its endpoints were exactly the 3 pod IPs.
- From a throwaway pod, `wget http://hello` returned the nginx welcome page. The name worked with no IP typed.
- After deleting a pod, the ClusterIP stayed the same, and the endpoint list swapped the old pod IP for the new one.

## Link to operating systems
A Service is like a socket address that stays valid while the process behind it is restarted. The name is the lookup, and the ClusterIP is the stable endpoint.

## Remember
- Pods come and go. A Service stays.
- Name (DNS) -> ClusterIP (stable) -> pod IP (changes).
- Labels connect a Service to its pods.
