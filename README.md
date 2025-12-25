# MyApp Manifest Repo
Single source of truth cho Kubernetes deployments.

## Structure
- `base/`: Shared manifests
- `overlays/on-premise/`: Harbor images cho on-prem cluster
- `overlays/cloud/`: GCP images cho GKE cluster
- `argocd/`: ArgoCD Application definitions

## Workflow
1. Jenkins update image tags trong overlays/
2. ArgoCD sync tự động từ main branch
