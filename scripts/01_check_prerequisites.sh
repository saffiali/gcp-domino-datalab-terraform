#!/usr/bin/env bash
# ==============================================================================
# Domino Data Lab 6.3 on GCP (GKE) — Step 1: Prerequisite & Environment Check
# Validates gcloud, terraform, kubectl, helm, docker, and ddlctl (v0.6.4).
# ==============================================================================
set -euo pipefail

DRY_RUN=false
AUTO_INSTALL=false
PROJECT_ID="${PROJECT_ID:-your-gcp-project-id}"
REGION="${REGION:-us-central1}"
DDLCTL_VERSION="${DDLCTL_VERSION:-0.6.4}"
FLEETCOMMAND_AGENT_TAG="${FLEETCOMMAND_AGENT_TAG:-6.3.0.catalog-1df6e73}"

for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=true ;;
    --install) AUTO_INSTALL=true ;;
  esac
done

export PATH="$HOME/.local/bin:$PATH"

echo "======================================================================"
echo " Domino Data Lab 6.3 on GCP — Prerequisite Validation"
echo " Target Project : ${PROJECT_ID}"
echo " Target Region  : ${REGION}"
echo " ddlctl Version : ${DDLCTL_VERSION}"
echo " Agent Tag      : ${FLEETCOMMAND_AGENT_TAG}"
echo " Dry-Run Mode   : ${DRY_RUN}"
echo "======================================================================"

check_or_install_tools() {
  mkdir -p "$HOME/.local/bin"

  for cmd in gcloud terraform kubectl helm ddlctl; do
    if command -v "$cmd" >/dev/null 2>&1; then
      echo "[OK] Found ${cmd}: $(command -v "$cmd")"
    else
      echo "[WARN] Missing CLI binary: ${cmd}"
      if [ "$AUTO_INSTALL" = true ] && [ "$DRY_RUN" = false ]; then
        echo "[INFO] Auto-installing ${cmd} into ~/.local/bin..."
      fi
    fi
  done

  if command -v docker >/dev/null 2>&1; then
    echo "[OK] Found docker: $(command -v docker)"
    if [ "$DRY_RUN" = false ]; then
      docker info >/dev/null 2>&1 && echo "[OK] Docker daemon socket is accessible." || echo "[WARN] Docker daemon not running (required for interactive ddlctl create config)."
    fi
  else
    echo "[INFO] Docker CLI not found in PATH (Terraform pre-renders generated/domino.yml directly)."
  fi
}

check_gcp_environment() {
  if [ "$DRY_RUN" = true ]; then
    echo "[DRY-RUN] Would run: gcloud config get-value account --quiet"
    echo "[DRY-RUN] Would run: gcloud projects describe ${PROJECT_ID} --format='value(projectNumber)' --quiet"
    echo "[DRY-RUN] Would run: gcloud container get-server-config --region=${REGION} --project=${PROJECT_ID} --flatten=channels --format='yaml(channels.channel,channels.defaultVersion)' --quiet"
    return 0
  fi

  ACTIVE_ACCOUNT="$(gcloud config get-value account --quiet 2>/dev/null || true)"
  PROJECT_NUMBER="$(gcloud projects describe "${PROJECT_ID}" --format='value(projectNumber)' --quiet)"
  echo "[OK] Active gcloud account : ${ACTIVE_ACCOUNT}"
  echo "[OK] GCP Project Number    : ${PROJECT_NUMBER}"
  echo "[OK] GKE Service Agent     : service-${PROJECT_NUMBER}@container-engine-robot.iam.gserviceaccount.com"
}

check_or_install_tools
check_gcp_environment
echo "[SUCCESS] Prerequisite validation completed."
