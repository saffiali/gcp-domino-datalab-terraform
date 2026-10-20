#!/usr/bin/env python3
"""Comprehensive automated validation suite for Domino Data Lab 6.3 on GCP (GKE)."""

import json
import pathlib
import subprocess
import sys
import yaml

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
TF_DIR = REPO_ROOT / "terraform"
K8S_DIR = REPO_ROOT / "k8s"
SCRIPTS_DIR = REPO_ROOT / "scripts"
ASSETS_DIR = REPO_ROOT / "assets"
GEN_DIR = REPO_ROOT / "generated"

REQUIRED_TF_FILES = [
    "versions.tf",
    "variables.tf",
    "apis.tf",
    "kms.tf",
    "network.tf",
    "gke.tf",
    "node_pools.tf",
    "storage.tf",
    "nfs-instance.tf",
    "gcnv.tf",
    "service-accounts.tf",
    "gcr.tf",
    "gcr-credential-refresher.tf",
    "dns.tf",
    "domino-config.tf",
    "outputs.tf",
    "terraform.tfvars.example",
    "examples/gke-main.tf",
]

REQUIRED_DDLCLOUD_OUTPUTS = [
    "google_filestore_ip_address",
    "google_filestore_file_share",
    "google_external_dns",
    "google_bucket_name",
    "google_project",
    "google_platform_service_account",
    "google_cluster_uuid",
    "google_gcr_service_account",
    "google_artifact_registry",
    "nfs_instance_ip",
    "nfs_instance_path",
    "gcr_credential_refresher",
    "gcnv_project_number",
    "gcnv_location",
    "gcnv_storage_pool_name",
    "gcnv_service_account_email",
    "gcnv_client_cidr",
    "gcnv_root_volume_name",
    "gcnv_export_policy_name",
]


def assert_check(condition: bool, message: str, results: list[tuple[bool, str]]) -> None:
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {message}")
    results.append((condition, message))


def main() -> int:
    results: list[tuple[bool, str]] = []
    print("=" * 74)
    print(" Domino Data Lab 6.3 on GCP (GKE) — Automated Verification Suite")
    print("=" * 74)

    # 1. Verify all Terraform files exist
    for rel_path in REQUIRED_TF_FILES:
        p = TF_DIR / rel_path
        assert_check(p.exists() and p.stat().st_size > 0, f"Terraform file exists: terraform/{rel_path}", results)

    # 2. Verify all 19 ddlcloud_generator_gke outputs are declared in outputs.tf
    outputs_text = (TF_DIR / "outputs.tf").read_text(encoding="utf-8")
    for out_name in REQUIRED_DDLCLOUD_OUTPUTS:
        assert_check(
            f'output "{out_name}"' in outputs_text,
            f"Domino 6.3 output declared in outputs.tf: {out_name}",
            results,
        )

    # 3. Verify KMS IAM binding includes both GCS and GKE service agents
    kms_text = (TF_DIR / "kms.tf").read_text(encoding="utf-8")
    assert_check(
        "container-engine-robot.iam.gserviceaccount.com" in kms_text
        and "gcs_account.email_address" in kms_text,
        "Cloud KMS IAM binding includes both GKE Service Agent and GCS Service Agent",
        results,
    )

    # 4. Verify Kubernetes manifests parse as valid YAML
    for k8s_file in sorted(K8S_DIR.glob("*.yaml")):
        docs = list(yaml.safe_load_all(k8s_file.read_text(encoding="utf-8")))
        assert_check(len(docs) > 0, f"Valid Kubernetes YAML manifest: k8s/{k8s_file.name} ({len(docs)} resources)", results)

    # 5. Verify rendered generated/domino.yml if present
    domino_yml_path = GEN_DIR / "domino.yml"
    if domino_yml_path.exists():
        domino_cfg = yaml.safe_load(domino_yml_path.read_text(encoding="utf-8"))
        assert_check(domino_cfg.get("schema") == "1.16", "generated/domino.yml uses Schema 1.16", results)
        assert_check(
            domino_cfg.get("storage_class", {}).get("block", {}).get("name") == "dominodisk"
            and domino_cfg.get("storage_class", {}).get("shared", {}).get("name") == "dominoshared",
            "generated/domino.yml defines dominodisk (block) and dominoshared (shared) StorageClasses",
            results,
        )
        assert_check(
            bool(domino_cfg.get("storage_class", {}).get("shared", {}).get("nfs", {}).get("server")),
            f"generated/domino.yml populated live NFS server IP: {domino_cfg.get('storage_class', {}).get('shared', {}).get('nfs', {}).get('server')}",
            results,
        )

    # 6. Verify shell scripts syntax via bash -n
    for script in sorted(SCRIPTS_DIR.glob("*.sh")):
        proc = subprocess.run(["bash", "-n", str(script)], capture_output=True, text=True)
        assert_check(proc.returncode == 0, f"Valid bash syntax: scripts/{script.name}", results)

    # 7. Verify horizontal-layered SVG and PNG architecture diagrams
    for idx in ["01", "02", "03"]:
        svg_matches = list(ASSETS_DIR.glob(f"{idx}_*.svg"))
        png_matches = list(ASSETS_DIR.glob(f"{idx}_*.png"))
        assert_check(
            len(svg_matches) == 1 and svg_matches[0].stat().st_size > 10000,
            f"Architecture SVG {idx} exists and is non-empty ({svg_matches[0].name if svg_matches else 'missing'})",
            results,
        )
        assert_check(
            len(png_matches) == 1 and png_matches[0].stat().st_size > 10000,
            f"Architecture PNG {idx} exists and is non-empty ({png_matches[0].name if png_matches else 'missing'})",
            results,
        )

    passed = sum(1 for ok, _ in results if ok)
    total = len(results)
    print("=" * 74)
    print(f" Verification Summary: {passed}/{total} checks passed.")
    print("=" * 74)
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
