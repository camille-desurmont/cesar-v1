# Kubernetes manifests

Apply files with `kubectl apply -f <file>` (or `-f deployment/kubernetes/` to apply all in the folder).

## Standard deployment (default)

- **API (2 replicas):** `api-deployment.yaml` + `api-service.yaml`
- **UI:** `ui-deployment.yaml` + `ui-service.yaml`

## Canary (new version with less traffic)

- Apply standard API + UI as above.
- Then apply `api-deployment-canary.yaml` and `api-service-canary.yaml`.
- Main traffic stays on `cesar-api`; route a small share (e.g. via Ingress) to `cesar-api-canary` to test the new version.

## Blue-green (instant switch)

- Use **only** the blue-green API files (do not use the standard api-deployment/api-service for the API):
  - `api-deployment-blue.yaml` + `api-deployment-green.yaml` + `api-service-blue-green.yaml`
- Service selector is `env: blue` by default. To switch to the new version, edit `api-service-blue-green.yaml`: set selector to `env: green`, then `kubectl apply -f api-service-blue-green.yaml`. Traffic goes to green. To roll back, set selector back to `env: blue` and apply again.
- UI: still use `ui-deployment.yaml` + `ui-service.yaml`.
