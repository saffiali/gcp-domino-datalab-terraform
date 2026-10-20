#!/usr/bin/env bash
# ==============================================================================
# Domino Data Lab 6.3 on GCP (GKE) — Step 4: Day-2 GKE & Domino Upgrade Runbook
# Follows:
#   - https://docs.domino.ai/6.3/admin/installation/manage-deployments/gcp/kubernetes-upgrade
#   - https://docs.domino.ai/6.3/admin/operations/upgrade-domino
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
GEN_DIR="${REPO_ROOT}/generated/pdb_backups"

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
TARGET_K8S_VERSION="${TARGET_K8S_VERSION:-1.35.6-gke.1250001}"
FLEETCOMMAND_AGENT_TAG="${FLEETCOMMAND_AGENT_TAG:-6.3.0.catalog-1df6e73}"

echo "======================================================================"
echo " Domino Data Lab 6.3 on GCP — GKE & Platform Operator Upgrade Utility"
echo " Cluster Name       : ${CLUSTER_NAME} (${LOCATION})"
echo " Target GKE Version : ${TARGET_K8S_VERSION}"
echo " Target Agent Tag   : ${FLEETCOMMAND_AGENT_TAG}"
echo " Dry-Run Mode       : ${DRY_RUN}"
echo "======================================================================"

if [ "$DRY_RUN" = true ]; then
  echo "[DRY-RUN] 1. Check for stalled/drifted HelmReleases prior to upgrade:"
  echo "  ddlctl get helmrelease -A --status stalled=true"
  echo "[DRY-RUN] 2. Back up and temporarily delete MongoDB PodDisruptionBudgets in domino-platform:"
  echo "  kubectl get pdb -n domino-platform mongodb-arbiter -o yaml > ${GEN_DIR}/mongodb-arbiter-pdb.yaml"
  echo "  kubectl get pdb -n domino-platform mongodb-primary -o yaml > ${GEN_DIR}/mongodb-primary-pdb.yaml"
  echo "  kubectl get pdb -n domino-platform mongodb-secondary -o yaml > ${GEN_DIR}/mongodb-secondary-pdb.yaml"
  echo "  kubectl delete pdb -n domino-platform mongodb-arbiter mongodb-primary mongodb-secondary"
  echo "[DRY-RUN] 3. Query valid GKE upgrade versions:"
  echo "  gcloud container get-server-config --region=${LOCATION} --project=${PROJECT_ID} --flatten=channels --format='yaml(channels.channel,channels.validVersions)' --limit=5 --quiet"
  echo "[DRY-RUN] 4. Upgrade GKE Control Plane and Node Pools (platform, compute, gpu):"
  echo "  gcloud container clusters upgrade ${CLUSTER_NAME} --master --cluster-version=${TARGET_K8S_VERSION} --region=${LOCATION} --project=${PROJECT_ID} --quiet"
  echo "  gcloud container clusters upgrade ${CLUSTER_NAME} --node-pool=platform --cluster-version=${TARGET_K8S_VERSION} --region=${LOCATION} --project=${PROJECT_ID} --quiet"
  echo "  gcloud container clusters upgrade ${CLUSTER_NAME} --node-pool=compute --cluster-version=${TARGET_K8S_VERSION} --region=${LOCATION} --project=${PROJECT_ID} --quiet"
  echo "  gcloud container clusters upgrade ${CLUSTER_NAME} --node-pool=gpu --cluster-version=${TARGET_K8S_VERSION} --region=${LOCATION} --project=${PROJECT_ID} --quiet"
  echo "[DRY-RUN] 5. Restore MongoDB PodDisruptionBudgets:"
  echo "  kubectl apply -f ${GEN_DIR}/mongodb-arbiter-pdb.yaml -f ${GEN_DIR}/mongodb-primary-pdb.yaml -f ${GEN_DIR}/mongodb-secondary-pdb.yaml"
  echo "[DRY-RUN] 6. Upgrade Domino CRD via ddlctl:"
  echo "  ddlctl upgrade domino --agent-version ${FLEETCOMMAND_AGENT_TAG}"
  exit 0
fi

mkdir -p "${GEN_DIR}"
for pdb in mongodb-arbiter mongodb-primary mongodb-secondary; do
  if kubectl get pdb -n domino-platform "$pdb" >/dev/null 2>&1; then
    kubectl get pdb -n domino-platform "$pdb" -o yaml > "${GEN_DIR}/${pdb}-pdb.yaml"
    kubectl delete pdb -n domino-platform "$pdb"
    echo "[OK] Backed up and removed PDB domino-platform/${pdb}"
  fi
done

echo "[INFO] Querying valid GKE versions in ${LOCATION}..."
gcloud container get-server-config --region="${LOCATION}" --project="${PROJECT_ID}" --flatten=channels --format="yaml(channels.channel,channels.validVersions)" --limit=5 --quiet

echo "[INFO] Restoring any backed up MongoDB PDBs..."
for pdb in mongodb-arbiter mongodb-primary mongodb-secondary; do
  if [ -f "${GEN_DIR}/${pdb}-pdb.yaml" ]; then
    kubectl apply -f "${GEN_DIR}/${pdb}-pdb.yaml"
  fi
done
