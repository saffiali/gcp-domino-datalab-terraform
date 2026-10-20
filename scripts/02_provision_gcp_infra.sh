#!/usr/bin/env bash
# ==============================================================================
# Domino Data Lab 6.3 on GCP (GKE) — Step 2: Provision GCP Infrastructure
# Runs terraform init, validate, plan, and (when --apply is passed) apply.
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
TF_DIR="${REPO_ROOT}/terraform"
GEN_DIR="${REPO_ROOT}/generated"

DRY_RUN=false
APPLY=false

for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=true ;;
    --apply)   APPLY=true ;;
  esac
done

export PATH="$HOME/.local/bin:$PATH"
mkdir -p "${GEN_DIR}"

echo "======================================================================"
echo " Domino Data Lab 6.3 on GCP — Terraform Infrastructure Provisioning"
echo " Terraform Dir : ${TF_DIR}"
echo " Dry-Run Mode  : ${DRY_RUN}"
echo " Apply Mode    : ${APPLY}"
echo "======================================================================"

if [ "$DRY_RUN" = true ]; then
  echo "[DRY-RUN] Would run: terraform -chdir=${TF_DIR} fmt -check"
  echo "[DRY-RUN] Would run: terraform -chdir=${TF_DIR} init"
  echo "[DRY-RUN] Would run: terraform -chdir=${TF_DIR} validate"
  echo "[DRY-RUN] Would run: terraform -chdir=${TF_DIR} plan -out=terraform.plan"
  if [ "$APPLY" = true ]; then
    echo "[DRY-RUN] Would run: terraform -chdir=${TF_DIR} apply -auto-approve terraform.plan"
  fi
  exit 0
fi

export GOOGLE_OAUTH_ACCESS_TOKEN="$(gcloud auth print-access-token --quiet)"

terraform -chdir="${TF_DIR}" fmt -check
terraform -chdir="${TF_DIR}" init
terraform -chdir="${TF_DIR}" validate
terraform -chdir="${TF_DIR}" plan -out=terraform.plan

if [ "$APPLY" = true ]; then
  echo "[INFO] Applying Terraform plan to provision Domino 6.3 GCP infrastructure..."
  terraform -chdir="${TF_DIR}" apply -auto-approve terraform.plan
  terraform -chdir="${TF_DIR}" output -json > "${GEN_DIR}/terraform-outputs.json"
  echo "[SUCCESS] Infrastructure provisioned and outputs saved to ${GEN_DIR}/terraform-outputs.json"
else
  echo "[INFO] Plan complete. Pass --apply to provision live GCP resources."
fi
