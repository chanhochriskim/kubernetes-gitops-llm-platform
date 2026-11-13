# Blog notes

Plain-language notes on what was built and learned in each session. Read them in order.

1. [The big picture](01-big-picture.md): what this project is and why
2. [Phase 0 walkthrough](02-phase-0-walkthrough.md): what we did, step by step
3. [Glossary](03-glossary.md): every term in one place
4. [Commands cheat sheet](04-commands-cheatsheet.md): the commands we used and what they do
5. [Review guide](05-review-guide.md): how to study these notes, with a quiz
6. [Phase 0 review session](06-phase-0-review-session.md): the Q&A we did, with wrong guesses and fixes
7. [Phase 1, step 1: Deployments](07-phase-1-deployments.md): the "I want 3 pods" loop
8. [Phase 1, step 2: Services](08-phase-1-services.md): a stable address for changing pods
9. [Phase 1, step 3: Probes](09-phase-1-probes.md): readiness vs liveness, tested by breaking a pod
10. [Phase 1, step 4: Rolling updates](10-phase-1-rolling-updates.md): a broken update stalls safely, then rolls back
11. [Phase 1, step 5: ConfigMaps and Secrets](11-phase-1-config-and-secrets.md): settings, secrets, and what base64 really is
12. [Phase 1, step 6: Postgres and storage](12-phase-1-postgres-storage.md): data that survives a deleted pod
13. [Phase 1, step 7: The backend and images](13-phase-1-backend-and-images.md): build an image, hit ImagePullBackOff, load it into Kind
14. [Phase 1, step 8: The frontend and chained Services](14-phase-1-frontend-and-service-chain.md): a reverse proxy between the browser and the backend
15. [Phase 1, step 9: Ingress](15-phase-1-ingress.md): the front door, and the scheduling detail we caught
16. [Phase 1, step 10: HTTPS with cert-manager](16-phase-1-https-cert-manager.md): certificates, CAs, and why curl said no
17. [Phase 2: GitOps with Argo CD](17-phase-2-argocd-gitops.md): a second reconcile loop, drift, and self-heal
18. [Phase 3, lesson 1: Limits, OOM and throttling](18-phase-3-limits-oom-and-throttling.md): the kernel kills for memory and slows for CPU
19. [Phase 3, lesson 2: QoS classes and limits through Git](19-phase-3-qos-and-limits-via-git.md): who the kernel kills first
20. [Phase 3, lesson 3: The HPA and a GitOps trap](20-phase-3-hpa-metrics-and-argocd.md): scaling up fast, down slowly, and two controllers fighting

These are written for a beginner. The more technical notes are in `../docs/`.
