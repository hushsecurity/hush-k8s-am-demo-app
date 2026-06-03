# hush-k8s-am-demo-app

Helm chart for validating that a Kubernetes environment and Hush Access Management
setup are operational end-to-end.

The chart deploys:
- Two pods:
  - `postgres` pod: PostgreSQL server seeded with sample data
  - `python-client` pod: Python workload that reads from Postgres
- Hush access resources for Postgres dynamic credential delivery to the Python client:
  - `AccessCredential` (postgres root credential)
  - `AccessPrivilege` (read access required by the client)
  - `AccessPolicy` (injects env vars into the client workload)
- Hush access resources for static secret delivery to the Python client:
  - `AccessCredential` (plaintext static secret)
  - `AccessPolicy` (injects `STATIC_SECRET` env var)

All resources are chart-managed and removed by `helm uninstall`, including both
pods, deployments, service account, configmaps, and Hush resources.

## Prerequisites

- Kubernetes cluster
- Helm 3
- Hush Access Management CRDs installed (`am.hush.security/v1alpha1`)
- Namespace `hush-security` exists (or set `.Values.hush.namespace` to an existing namespace)

## Install

```bash
helm install demo-app oci://ghcr.io/hushsecurity/hush-am-demo-app
```

## Validate

```bash
kubectl logs -n goat-apps -l app.kubernetes.io/component=client -c python-client -f
```

Expected behavior:
- Client waits for Postgres
- Client reads from `users` table
- Client logs whether `STATIC_SECRET` is present

## Uninstall

```bash
helm uninstall demo-app
```

This removes all chart-managed resources and leaves no chart-created workload objects behind.

## Notes

- The chart intentionally uses ephemeral Postgres storage (`emptyDir`) for a no-trace
  test footprint.
