# Phase 1, step 10: HTTPS with cert-manager

## The problem
Over plain `http://`, anyone on the network path can read the traffic. HTTPS encrypts it. That needs a certificate.

## Certificates and who vouches for them
A **certificate** is a file that says "this public key belongs to `app.local`". It is signed by a **Certificate Authority (CA)**, someone the client already trusts. Browsers and tools ship with a list of trusted CAs.

Encryption alone is not enough. Without a trusted signer, a client cannot know it is talking to the real server and not an impostor. Trust comes from who signed the certificate.

## cert-manager
**cert-manager** is a controller that creates and renews certificates. You describe the certificate you want, and it makes the key, gets it signed, and stores both in a Secret. It installed 3 pods and taught the cluster new object types (`Certificate`, `Issuer`, `ClusterIssuer` and others). Those definitions are called CRDs.

## The chain we built (`manifests/phase1/tls.yaml`)
1. `selfsigned-issuer`: an issuer that signs with its own key.
2. `local-ca`: a CA certificate, signed by the self-signed issuer. This is our own private authority.
3. `local-ca-issuer`: an issuer that signs using `local-ca`.
4. `app-local`: a certificate for `app.local`, signed by `local-ca-issuer`. cert-manager stored it in the Secret `app-local-tls`.

The Ingress got a `tls:` section pointing at `app-local-tls`, and the ingress controller started serving HTTPS with it. The private keys live in Secrets in the cluster, not in Git.

## What we saw
- Without trusting our CA, curl refused: `unable to get local issuer certificate`.
- After giving curl our CA file (`--cacert`), the page and `/api/chat` worked over HTTPS.
- The certificate showed issuer `CN=local-ca`, name `app.local`, valid for about 90 days. cert-manager renews it before it expires.
- `Verify return code: 0 (ok)`.

A browser would show a warning for the same reason curl refused: it does not know our CA. To avoid the warning, you would add the CA file to your system's trusted list. We skipped the browser step, so this was tested with curl only.

## Remember
- Encryption needs a certificate. Trust needs a signer you already trust.
- A self-signed CA is fine for learning and wrong for the public internet.
- cert-manager turns "I want a certificate" into a renewing, automatic process. It is another reconcile loop.
- A Secret named in the Ingress is how the front door gets its certificate.
