#!/usr/bin/env bash
# ==============================================================================
# Domino Data Lab 6.3 on GCP (GKE) — Step 3: Deploy Domino Platform on GKE
# Follows https://docs.domino.ai/6.3/admin/installation/manage-deployments/gcp/deploy
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
GEN_DIR="${REPO_ROOT}/generated"
K8S_DIR="${REPO_ROOT}/k8s"

DRY_RUN=false
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=true ;;
  esac
done

export PATH="$HOME/.local/bin:$PATH"

PROJECT_ID="${PROJECT_ID:-your-gcp-project-id}"
CLUSTER_NAME="${CLUSTER_NAME:-domino-gcp}"
LOCATION="${LOCATION:-us-central1}"
DOMINO_HOSTNAME="${DOMINO_HOSTNAME:-domino.gke-demos.example.com}"
FLEETCOMMAND_AGENT_TAG="${FLEETCOMMAND_AGENT_TAG:-6.3.0.catalog-1df6e73}"

echo "======================================================================"
echo " Domino Data Lab 6.3 on GCP — Platform Operator & Domino CRD Deployment"
echo " Project ID   : ${PROJECT_ID}"
echo " Cluster Name : ${CLUSTER_NAME} (${LOCATION})"
echo " Agent Tag    : ${FLEETCOMMAND_AGENT_TAG}"
echo " Dry-Run Mode : ${DRY_RUN}"
echo "======================================================================"

if [ "$DRY_RUN" = true ]; then
  echo "[DRY-RUN] 1. Configure kubeconfig:"
  echo "  gcloud container clusters get-credentials ${CLUSTER_NAME} --region=${LOCATION} --project=${PROJECT_ID} --quiet"
  echo "[DRY-RUN] 2. Apply Domino namespaces, StorageClasses, and external-nginx NetworkPolicy:"
  echo "  kubectl apply -f ${K8S_DIR}/01_domino_namespaces_and_storageclasses.yaml"
  echo "  kubectl apply -f ${K8S_DIR}/02_external_nginx_network_policy.yaml"
  echo "[DRY-RUN] 3. Create TLS secret domino-platform/my-cert:"
  echo "  kubectl create secret tls my-cert --cert=${GEN_DIR}/tls.crt --key=${GEN_DIR}/tls.key -n domino-platform"
  echo "[DRY-RUN] 4. Bootstrap Domino Platform Operator (v0.6.4):"
  echo "  ddlctl bootstrap --skip-domino-resource --username \"\$QUAY_USERNAME\" --password \"\$QUAY_PASSWORD\""
  echo "[DRY-RUN] 5. Create Domino Custom Resource using rendered ${GEN_DIR}/domino.yml:"
  echo "  ddlctl create domino --config ${GEN_DIR}/domino.yml --agent-version ${FLEETCOMMAND_AGENT_TAG}"
  echo "[DRY-RUN] 6. Inspect HelmReleases & retrieve Keycloak initial password:"
  echo "  ddlctl get domino"
  echo "  ddlctl get helmrelease --all"
  echo "  kubectl get secret -n domino-platform keycloak-http -o jsonpath='{.data.password}' | base64 -d"
  exit 0
fi

# 1. Configure KUBECONFIG
LOC_PARTS=$(echo "${LOCATION}" | awk -F'-' '{print NF}')
if [ "$LOC_PARTS" -eq 2 ]; then
  gcloud container clusters get-credentials "${CLUSTER_NAME}" --region="${LOCATION}" --project="${PROJECT_ID}" --quiet
else
  gcloud container clusters get-credentials "${CLUSTER_NAME}" --zone="${LOCATION}" --project="${PROJECT_ID}" --quiet
fi

# 2. Apply namespaces, StorageClass, and NetworkPolicies
kubectl apply -f "${K8S_DIR}/01_domino_namespaces_and_storageclasses.yaml"
kubectl apply -f "${K8S_DIR}/02_external_nginx_network_policy.yaml"
kubectl apply -f "${K8S_DIR}/03_custom_certificates_configmap.yaml"
kubectl apply -f "${K8S_DIR}/04_distributed_clusters_workspace_tools.yaml"

# 3. Create self-signed TLS certificate if not already present in domino-platform/my-cert
mkdir -p "${GEN_DIR}"
if ! kubectl get secret my-cert -n domino-platform >/dev/null 2>&1; then
  openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout "${GEN_DIR}/tls.key" \
    -out "${GEN_DIR}/tls.crt" \
    -subj "/CN=${DOMINO_HOSTNAME}/O=DominoDataLab" >/dev/null 2>&1
  kubectl create secret tls my-cert \
    --cert="${GEN_DIR}/tls.crt" \
    --key="${GEN_DIR}/tls.key" \
    -n domino-platform
  echo "[OK] Created TLS secret domino-platform/my-cert"
else
  echo "[OK] TLS secret domino-platform/my-cert already exists"
fi

# 4. Back up domino.yml before deployment
if [ -f "${GEN_DIR}/domino.yml" ]; then
  cp "${GEN_DIR}/domino.yml" "${GEN_DIR}/domino.yml.backup-$(date +%Y-%m-%d_%H-%M-%S)"
  echo "[OK] Backed up ${GEN_DIR}/domino.yml"
fi

# 5. Bootstrap Domino Platform Operator if QUAY_USERNAME & QUAY_PASSWORD are provided
if [ -n "${QUAY_USERNAME:-}" ] && [ -n "${QUAY_PASSWORD:-}" ]; then
  echo "[INFO] Bootstrapping Domino Platform Operator..."
  ddlctl bootstrap --skip-domino-resource --username "${QUAY_USERNAME}" --password "${QUAY_PASSWORD}"
  ddlctl create domino --config "${GEN_DIR}/domino.yml" --agent-version "${FLEETCOMMAND_AGENT_TAG}"
else
  echo "[INFO] QUAY_USERNAME / QUAY_PASSWORD not set in environment; Kubernetes namespaces, StorageClass, NetworkPolicies, and TLS secret are configured and ready for ddlctl bootstrap."
fi
