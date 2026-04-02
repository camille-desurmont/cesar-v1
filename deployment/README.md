# CESAR deployment

This folder contains everything to run CESAR in containers and on Kubernetes: **Docker** images, **docker-compose** for local runs, and **Kubernetes** YAML for the API, UI, and two rollout strategies (canary, blue-green).

---

## Quick reference

| What you need | Use |
|---------------|-----|
| Run API + UI on your machine with one command | `docker compose -f deployment/docker-compose.yml up` (from repo root) |
| Build API image | `docker build -f deployment/Dockerfile.api -t cesar-api:latest .` |
| Build UI image | `docker build -f deployment/Dockerfile.ui -t cesar-ui:latest .` (from repo root; Dockerfile copies `runtime/` and `prediction_contract/`) |
| Deploy API + UI on Kubernetes (standard) | `kubectl apply -f deployment/kubernetes/api-deployment.yaml -f deployment/kubernetes/api-service.yaml -f deployment/kubernetes/ui-deployment.yaml -f deployment/kubernetes/ui-service.yaml` |
| Try a new API version with minimal risk (canary) | Apply canary deployment + service; send a fraction of traffic to `cesar-api-canary` |
| Switch to a new API version with no downtime (blue-green) | Use blue + green deployments and one service; change the service selector from `env: blue` to `env: green` |

---

## Kubernetes files in brief

- **Deployment** = “run this container in N copies (pods)”. Kubernetes restarts failed pods and keeps the desired number running.
- **Service** = stable name (e.g. `cesar-api`) and load-balancing across the pods that match its selector (labels).

The API is run with **2 replicas** so that traffic is shared and a single pod failure doesn’t take down the API.

### Standard rollout (no canary / blue-green)

- `api-deployment.yaml` – API, 2 replicas, label `version: stable`
- `api-service.yaml` – Service for the API (selector `version: stable`)
- `ui-deployment.yaml` – UI, 1 replica
- `ui-service.yaml` – Service for the UI

Apply all four when you only want a normal deployment.

### Canary rollout

You run the **current** version as usual (api-deployment + api-service) and a **new** version as a canary with fewer replicas (e.g. 1). Part of the traffic (e.g. 10%) goes to the canary; the rest to the stable API. If the canary behaves well, you roll out the new image to the main deployment.

- `api-deployment-canary.yaml` – same app, 1 replica, label `version: canary`, image e.g. `cesar-api:canary`
- `api-service-canary.yaml` – Service that selects `version: canary`

Apply the canary deployment and canary service. The main Service still points at `version: stable`. To send part of the traffic to the canary you need something in front (e.g. an Ingress with two backends and weight-based routing, or a proxy). After testing, update the main deployment to the new image and scale down or remove the canary.

### Blue-green rollout

You have **two** full deployments (e.g. “blue” and “green”), each with 2 replicas. One is live; the other is the next version. You switch by changing the **Service selector** from one to the other. No gradual traffic shift: instant cutover.

- `api-deployment-blue.yaml` – API “blue”, 2 replicas, label `env: blue`
- `api-deployment-green.yaml` – API “green”, 2 replicas, label `env: green` (use your new image tag here)
- `api-service-blue-green.yaml` – Single Service; selector is `env: blue` (or `env: green`). **To switch:** edit the selector to `env: green`, apply, and traffic goes to green. To roll back, set it back to `env: blue` and apply.

You don’t use `api-service.yaml` when using blue-green; use `api-service-blue-green.yaml` instead.

---

## Docker Compose (local)

`docker-compose.yml` builds and runs the API and UI. The API expects model/contract under `/artifacts`; the compose file mounts `./artifact_storage` there. Start the API and UI:

```bash
# From repo root
docker compose -f deployment/docker-compose.yml up --build
```

Then open the UI at http://localhost:8080 and the API at http://localhost:8000 (if exposed). Adjust ports in the compose file if needed.
