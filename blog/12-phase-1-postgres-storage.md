# Phase 1, step 6: Postgres and persistent storage

## The problem
A stateless pod can be deleted and replaced with no loss. A database cannot. Files written inside a pod's container disappear when the pod is replaced. The data has to live somewhere that outlasts the pod.

## The pieces
- **StatefulSet:** like a Deployment, but for stateful apps. The pod gets a stable name (`postgres-0`) that is the same after a restart.
- **PersistentVolumeClaim (PVC):** a request for storage: "I need 1 GB that outlives my pod."
- **PersistentVolume (PV):** the actual storage that fills the request. Kind creates it automatically through its default storage class.
- **Headless Service:** a Service with no virtual IP (`clusterIP: None`). It gives each StatefulSet pod a stable DNS name.

The data lives in the PV, not in the pod. The new pod reattaches to the same claim.

## What we ran
`manifests/phase1/postgres.yaml`: one Postgres pod. The password is in a Secret created from the command line (a throwaway value for this demo, not in Git). A `volumeClaimTemplates` section makes a claim for each pod (`data-postgres-0`).

## What we saw
1. Kubernetes created the claim and the volume, and marked them `Bound`.
2. We created a table and inserted two rows.
3. We deleted the pod. A new pod with the **same name** (`postgres-0`) started, but with a new internal ID.
4. We queried the new pod. Both rows were there.
5. The data was a 39 MB directory on the worker node's own disk (`/var/local-path-provisioner/...`).

## The OS link
A volume is a directory on disk that Kubernetes mounts into the container, like mounting a filesystem. The container process comes and goes, and the files stay. This is the same reason a program's files survive after the program exits.

## A limit of this setup
This local storage is tied to one node. If that node were lost, so would the data. A real cluster uses network storage or database replication to avoid this. For learning, we use the simple version.

## Deployment vs. StatefulSet
- Deployment: pods are interchangeable. Names are random. Good for stateless apps.
- StatefulSet: pods have identity. Names are stable (`postgres-0`). Each gets its own storage. Good for databases.

## Remember
- Pod storage is temporary. A volume outlasts the pod.
- The claim is the request. The volume is the supply.
- A StatefulSet keeps a pod's name and its data together.
