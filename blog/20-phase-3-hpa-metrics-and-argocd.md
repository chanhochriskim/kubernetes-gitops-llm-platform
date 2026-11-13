# Phase 3, lesson 3: Autoscaling with the HPA, and a GitOps trap

## metrics-server
`kubectl top` failed with "Metrics API not available". Kubernetes does not collect usage numbers by default. **metrics-server** does. We vendored v0.9.1 (`manifests/phase3/metrics-server/`) with one patch: `--kubelet-insecure-tls`. Kind's kubelet certificates are not signed by a CA that metrics-server trusts, so the flag skips that check. That is fine for a local throwaway cluster and wrong for production.

At idle the backend used about 5 to 7m CPU (its request is 50m).

## The HPA
`manifests/phase3/hpa-backend.yaml` says: keep the backend's average CPU at about 50% of its request, with 2 to 5 pods.

The formula: desired pods = ceil(current pods x current CPU % / target CPU %). It checks about every 15 seconds.

## What we saw (load from `manifests/phase3/loadgen.yaml`, two busybox pods in a loop; a lighter choice than Locust for a laptop)
- CPU on the backend went from 8% of request to several hundred percent.
- The first scale-up went 2 to 4, then to the cap of 5. The cap `maxReplicas: 5` held even though the formula asked for more.
- After the load stopped, CPU fell below the target within about 90 seconds. The pods stayed at 5 for about 5 minutes, and then dropped to 4. After about 7 minutes it was still on its way down to 2.

Scaling up is quick and scaling down is slow on purpose. The HPA has a stabilization window of 5 minutes by default for scaling down: it uses the highest pod count it wanted over that window. This avoids flapping when load briefly dips. We did not measure the full time to reach 2.

## The GitOps trap
Git said the backend Deployment had `replicas: 2`, and Argo CD had self-heal on. When the HPA scaled up, the cluster event log showed Argo CD reverting it to 2 (for example 5 to 2), and the HPA scaling up again within seconds. The two controllers undid each other's work, which means pods were being created and killed for no reason. Later Argo CD showed `OutOfSync` and stopped reverting. We do not know exactly why it stopped.

## The fix
One owner for the replica count. We:
1. Removed `replicas` from `deploy/app/backend.yaml` and left a comment about why.
2. Added the HPA to `deploy/app/` so it lives in Git.

After the push, Argo CD stayed `Synced` and did not fight the HPA.

## A side effect we saw
In the first sample after the sync, the Deployment briefly showed 1 replica. Taking `replicas` out of a manifest that had it before resets the field to its default of 1, and the HPA then brought it back to the minimum of 2 within seconds. For a moment, that is a single pod. On a production system you would avoid that dip, for example by removing the field in a quiet period or by using Argo CD's `ignoreDifferences` for `/spec/replicas`. We then saw the pods rise to 4 shortly after, which is the HPA still remembering the earlier high load.

## Remember
- The HPA needs metrics-server, and it needs a CPU request to compute a percentage.
- Up fast, down slow, on purpose.
- Two controllers must not own the same field. Pick one.
- Take a field out of Git with care. The cluster can reset it.
