#!/usr/bin/env python3
"""Generates 3 publication-grade HORIZONTAL-LAYERED SVG & PNG architecture diagrams for Domino Data Lab 6.3 on GCP."""

import base64
import pathlib
import shutil
import subprocess

ICON_DIR = pathlib.Path(
    "/google/src/cloud/saffi/deploy_domino_gcp_terraform/google3/"
    "googledata/html/external_content/gstatic/cgc/shared/product-icons"
)
FALLBACK_ICON_DIR = pathlib.Path(
    "/google/src/files/head/depot/google3/"
    "googledata/html/external_content/gstatic/cgc/shared/product-icons"
)
REPO_ROOT = pathlib.Path(
    "/usr/local/google/home/saffi/teamwork_projects/domino_datalab_gcp_terraform"
)
ASSETS_DIR = REPO_ROOT / "assets"


def load_icon_data_uri(name: str) -> str:
    path = ICON_DIR / name / f"{name}.png"
    if not path.exists():
        path = FALLBACK_ICON_DIR / name / f"{name}.png"
    raw = path.read_bytes()
    b64 = base64.b64encode(raw).decode("ascii")
    return f"data:image/png;base64,{b64}"


def build_svg_1_reference_architecture(icons: dict[str, str]) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 1040" width="100%" height="100%">
  <defs>
    <style>
      .title {{ font: 700 22px 'Google Sans', 'Inter', 'Segoe UI', Arial, sans-serif; fill: #0f172a; }}
      .subtitle {{ font: 500 13px 'Google Sans', 'Inter', 'Segoe UI', Arial, sans-serif; fill: #475569; }}
      .card-title {{ font: 700 13px 'Google Sans', 'Inter', 'Segoe UI', Arial, sans-serif; fill: #0f172a; }}
      .card-body {{ font: 500 11px 'Google Sans', 'Inter', 'Segoe UI', Arial, sans-serif; fill: #334155; }}
      .card-mono {{ font: 600 10.2px 'Roboto Mono', monospace; fill: #0f172a; }}
      .badge {{ font: 700 10.8px 'Roboto Mono', monospace; fill: #ffffff; }}
    </style>
    <filter id="shadow" x="-2%" y="-4%" width="104%" height="110%">
      <feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#0f172a" flood-opacity="0.07"/>
    </filter>
    <marker id="arrow-blue" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#1d4ed8"/>
    </marker>
    <marker id="arrow-purple" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#7c3aed"/>
    </marker>
    <marker id="arrow-green" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#059669"/>
    </marker>
    <marker id="arrow-orange" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#d97706"/>
    </marker>
  </defs>

  <rect width="1600" height="1040" rx="16" fill="#f8fafc" stroke="#cbd5e1" stroke-width="2"/>

  <!-- Top Header Banner -->
  <rect x="20" y="16" width="1560" height="64" rx="12" fill="#ffffff" stroke="#e2e8f0" stroke-width="1.5" filter="url(#shadow)"/>
  <rect x="20" y="16" width="10" height="64" rx="4" fill="#1a73e8"/>
  <text x="46" y="44" class="title">Domino Data Lab 6.3 on Google Cloud Platform (GKE 1.35) — Reference Architecture</text>
  <text x="46" y="65" class="subtitle">Project: your-gcp-project-id (123456789012)  |  4 Horizontal Layers Stacked Top-to-Bottom: Ingress -&gt; Platform Control Plane -&gt; Compute Grid -&gt; Shared Storage &amp; CMEK</text>

  <!-- Outer GCP VPC Perimeter -->
  <rect x="20" y="96" width="1560" height="926" rx="14" fill="#f1f5f9" stroke="#2563eb" stroke-width="2.5" stroke-dasharray="10,6"/>
  <rect x="40" y="85" width="760" height="22" rx="6" fill="#1d4ed8"/>
  <text x="52" y="100" class="badge">GCP PROJECT: your-gcp-project-id  |  CUSTOM VPC: domino-gcp (10.138.0.0/20)  |  GKE 1.35 STABLE CHANNEL</text>

  <!-- ===================================================================== -->
  <!-- HORIZONTAL LAYER 1 (TOP): EXTERNAL HTTPS INGRESS, DNS & TLS           -->
  <!-- ===================================================================== -->
  <rect x="36" y="118" width="1528" height="186" rx="12" fill="#eff6ff" stroke="#3b82f6" stroke-width="2" filter="url(#shadow)"/>
  <rect x="36" y="118" width="1528" height="32" rx="10" fill="#1d4ed8"/>
  <text x="54" y="139" class="badge">LAYER 1 (TOP BAND) — EXTERNAL HTTPS INGRESS, CLOUD DNS, TLS TERMINATION &amp; NETWORK POLICY (dns.tf | k8s/02)</text>

  <!-- Card 1A -->
  <rect x="52" y="160" width="346" height="130" rx="10" fill="#ffffff" stroke="#bfdbfe" stroke-width="1.5" filter="url(#shadow)"/>
  <image href="{icons['virtual_private_cloud']}" x="64" y="174" width="36" height="36"/>
  <text x="110" y="184" class="card-title">1A. Data Scientists &amp; Admins</text>
  <text x="110" y="200" class="card-body">HTTPS / WebSockets (WSS) Clients</text>
  <text x="68" y="224" class="card-mono">• Web Browser (Domino UI &amp; Workspaces)</text>
  <text x="68" y="242" class="card-mono">• Domino CLI (domino sync / domino run)</text>
  <text x="68" y="260" class="card-mono">• Model Endpoint REST API Consumers</text>
  <text x="68" y="278" class="card-mono">• Keycloak Admin (/auth/ DominoRealm)</text>

  <!-- Card 1B -->
  <rect x="416" y="160" width="356" height="130" rx="10" fill="#ffffff" stroke="#bfdbfe" stroke-width="1.5" filter="url(#shadow)"/>
  <image href="{icons['cloud_dns']}" x="428" y="174" width="36" height="36"/>
  <text x="474" y="184" class="card-title">1B. Cloud DNS &amp; Static Global IP</text>
  <text x="474" y="200" class="card-mono">dns.tf | google_dns_record_set</text>
  <text x="432" y="224" class="card-body">• Dedicated FQDN (Not Subdomain of Domino)</text>
  <text x="432" y="242" class="card-mono">• DNS A &amp; CAA Records (letsencrypt.org)</text>
  <text x="432" y="260" class="card-mono">• Optional external-dns Workload Identity</text>
  <text x="432" y="278" class="card-mono">• Optional cert-manager Workload Identity</text>

  <!-- Card 1C -->
  <rect x="790" y="160" width="366" height="130" rx="10" fill="#ffffff" stroke="#2563eb" stroke-width="2" filter="url(#shadow)"/>
  <image href="{icons['cloud_load_balancing']}" x="802" y="174" width="38" height="38"/>
  <text x="850" y="184" class="card-title">1C. External HTTPS Load Balancer</text>
  <text x="850" y="200" class="card-mono">Service: nginx-ingress-controller (LB)</text>
  <text x="806" y="224" class="card-body">• Forwards TCP :80 (HTTP) &amp; :443 (HTTPS)</text>
  <text x="806" y="242" class="card-body">• Health Check Path: /healthz (HTTP 200)</text>
  <text x="806" y="260" class="card-mono">• WebSockets Timeout: 3600s (Jupyter/VSCode)</text>
  <text x="806" y="278" class="card-mono">• Header: X-Forwarded-Proto: https</text>

  <!-- Card 1D -->
  <rect x="1174" y="160" width="374" height="130" rx="10" fill="#ffffff" stroke="#bfdbfe" stroke-width="1.5" filter="url(#shadow)"/>
  <image href="{icons['cloud_armor']}" x="1186" y="174" width="36" height="36"/>
  <text x="1232" y="184" class="card-title">1D. TLS &amp; NetworkPolicy Gate</text>
  <text x="1232" y="200" class="card-mono">k8s/02 &amp; k8s/03 Manifests</text>
  <text x="1190" y="224" class="card-mono">• Secret: domino-platform/my-cert (TLS)</text>
  <text x="1190" y="242" class="card-mono">• ConfigMap: default/domino-custom-certificates</text>
  <text x="1190" y="260" class="card-mono">• Mount: /etc/ssl/certs/domino-custom</text>
  <text x="1190" y="278" class="card-mono">• NetworkPolicy: external-nginx (Ingress)</text>

  <path d="M 398 225 L 414 225" stroke="#1d4ed8" stroke-width="2.5" marker-end="url(#arrow-blue)"/>
  <path d="M 772 225 L 788 225" stroke="#1d4ed8" stroke-width="2.5" marker-end="url(#arrow-blue)"/>
  <path d="M 1156 225 L 1172 225" stroke="#1d4ed8" stroke-width="2.5" marker-end="url(#arrow-blue)"/>

  <!-- ===================================================================== -->
  <!-- HORIZONTAL LAYER 2: GKE 1.35 CONTROL PLANE & DOMINO PLATFORM TIER     -->
  <!-- ===================================================================== -->
  <rect x="36" y="324" width="1528" height="214" rx="12" fill="#f5f3ff" stroke="#8b5cf6" stroke-width="2" filter="url(#shadow)"/>
  <rect x="36" y="324" width="1528" height="32" rx="10" fill="#7c3aed"/>
  <text x="54" y="345" class="badge">LAYER 2 (SECOND BAND) — PRIVATE GKE 1.35 CONTROL PLANE &amp; DOMINO PLATFORM TIER (gke.tf | Namespaces: domino-platform &amp; domino-system)</text>

  <!-- Card 2A -->
  <rect x="52" y="368" width="356" height="156" rx="10" fill="#ffffff" stroke="#ddd6fe" stroke-width="1.5" filter="url(#shadow)"/>
  <image href="{icons['google_kubernetes_engine']}" x="64" y="382" width="38" height="38"/>
  <text x="112" y="392" class="card-title">2A. Regional Private GKE 1.35</text>
  <text x="112" y="408" class="card-mono">Cluster: domino-gcp (us-central1)</text>
  <text x="68" y="432" class="card-body">• Kubernetes 1.35 (STABLE Release Channel)</text>
  <text x="68" y="450" class="card-mono">• Master CIDR: 172.16.1.0/28 (Private Nodes)</text>
  <text x="68" y="468" class="card-mono">• Dataplane V2 (ADVANCED_DATAPATH) + VPA</text>
  <text x="68" y="486" class="card-mono">• KMS etcd Encryption: ENCRYPTED</text>
  <text x="68" y="504" class="card-mono">• Webhooks: 6443,8080,8443,9443,10250,15017</text>

  <!-- Card 2B -->
  <rect x="424" y="368" width="360" height="156" rx="10" fill="#ffffff" stroke="#7c3aed" stroke-width="2" filter="url(#shadow)"/>
  <image href="{icons['google_kubernetes_engine']}" x="436" y="382" width="38" height="38"/>
  <text x="484" y="392" class="card-title">2B. Domino Platform Operator</text>
  <text x="484" y="408" class="card-mono">Namespace: domino-operator (ddlctl v0.6.4)</text>
  <text x="440" y="432" class="card-mono">• Agent: 6.3.0.catalog-1df6e73</text>
  <text x="440" y="450" class="card-body">• Reconciles Domino CRD (.spec.config)</text>
  <text x="440" y="468" class="card-body">• 5-Min HelmRelease Drift Detection Loop</text>
  <text x="440" y="486" class="card-mono">• ddlctl get / diff / reconcile helmrelease</text>
  <text x="440" y="504" class="card-mono">• Schema: 1.16 (generated/domino.yml)</text>

  <!-- Card 2C -->
  <rect x="800" y="368" width="364" height="156" rx="10" fill="#ffffff" stroke="#ddd6fe" stroke-width="1.5" filter="url(#shadow)"/>
  <image href="{icons['compute_engine']}" x="812" y="382" width="38" height="38"/>
  <text x="860" y="392" class="card-title">2C. Platform Node Pool (platform)</text>
  <text x="860" y="408" class="card-mono">dominodatalab.com/node-pool=platform</text>
  <text x="816" y="432" class="card-body">• Standard Tier (300 Execs): 4x n2-highmem-8</text>
  <text x="816" y="450" class="card-body">• Large Tier (600 Execs): 5x n2-highmem-16</text>
  <text x="816" y="468" class="card-mono">• 8–16 vCPU | 64 GB RAM | 128 GB pd-balanced</text>
  <text x="816" y="486" class="card-mono">• COS_CONTAINERD + GCFS Image Streaming</text>
  <text x="816" y="504" class="card-mono">• Zones: us-central1-a, us-central1-b (max 60 pods)</text>

  <!-- Card 2D -->
  <rect x="1180" y="368" width="368" height="156" rx="10" fill="#ffffff" stroke="#ddd6fe" stroke-width="1.5" filter="url(#shadow)"/>
  <image href="{icons['identity_and_access_management']}" x="1192" y="382" width="38" height="38"/>
  <text x="1240" y="392" class="card-title">2D. Core Platform Microservices</text>
  <text x="1240" y="408" class="card-mono">Namespace: domino-platform</text>
  <text x="1196" y="432" class="card-mono">• Nucleus Dispatcher/Frontend &amp; Domino API</text>
  <text x="1196" y="450" class="card-mono">• Keycloak Identity (/auth/ DominoRealm SSO)</text>
  <text x="1196" y="468" class="card-mono">• MongoDB ReplicaSet + PostgreSQL + Vault</text>
  <text x="1196" y="486" class="card-mono">• RabbitMQ HA + Elasticsearch + Git Server</text>
  <text x="1196" y="504" class="card-mono">• MLflow Registry + GCR Cred Refresher</text>

  <!-- ===================================================================== -->
  <!-- HORIZONTAL LAYER 3: ELASTIC COMPUTE GRID & DISTRIBUTED CLUSTERS       -->
  <!-- ===================================================================== -->
  <rect x="36" y="558" width="1528" height="214" rx="12" fill="#ecfdf5" stroke="#10b981" stroke-width="2" filter="url(#shadow)"/>
  <rect x="36" y="558" width="1528" height="32" rx="10" fill="#059669"/>
  <text x="54" y="579" class="badge">LAYER 3 (THIRD BAND) — ELASTIC COMPUTE GRID, DISTRIBUTED HPC CLUSTERS &amp; IMAGE BUILDERS (node_pools.tf | Namespace: domino-compute)</text>

  <!-- Card 3A -->
  <rect x="52" y="602" width="356" height="156" rx="10" fill="#ffffff" stroke="#a7f3d0" stroke-width="1.5" filter="url(#shadow)"/>
  <image href="{icons['compute_engine']}" x="64" y="616" width="38" height="38"/>
  <text x="112" y="626" class="card-title">3A. Compute Node Pool (compute)</text>
  <text x="112" y="642" class="card-mono">dominodatalab.com/node-pool=default</text>
  <text x="68" y="666" class="card-body">• Machine: n2-highmem-8 (8 vCPU, 64 GB RAM)</text>
  <text x="68" y="684" class="card-mono">• Boot Disk: 400 GB pd-balanced (10x Image Rule)</text>
  <text x="68" y="702" class="card-mono">• Labels: domino/build-node=true</text>
  <text x="68" y="720" class="card-mono">• Autoscaling: min=0, max=10/zone (max 30 pods)</text>
  <text x="68" y="738" class="card-mono">• GCFS Container Image Streaming Enabled</text>

  <!-- Card 3B -->
  <rect x="424" y="602" width="360" height="156" rx="10" fill="#ffffff" stroke="#059669" stroke-width="2" filter="url(#shadow)"/>
  <image href="{icons['google_kubernetes_engine']}" x="436" y="616" width="38" height="38"/>
  <text x="484" y="626" class="card-title">3B. Workspaces, Jobs, Apps &amp; APIs</text>
  <text x="484" y="642" class="card-mono">Ephemeral User Execution Pods</text>
  <text x="440" y="666" class="card-body">• IDEs: JupyterLab, Jupyter, RStudio, VS Code</text>
  <text x="440" y="684" class="card-body">• Apps: Flask, FastAPI, Streamlit, Shiny, Dash</text>
  <text x="440" y="702" class="card-body">• Low-Latency Real-Time &amp; Async Model Endpoints</text>
  <text x="440" y="720" class="card-mono">• Data Plane Agent + Cluster Autoscaler</text>
  <text x="440" y="738" class="card-mono">• Optional Nexus Remote Data Plane Support</text>

  <!-- Card 3C -->
  <rect x="800" y="602" width="364" height="156" rx="10" fill="#ffffff" stroke="#a7f3d0" stroke-width="1.5" filter="url(#shadow)"/>
  <image href="{icons['google_kubernetes_engine']}" x="812" y="616" width="38" height="38"/>
  <text x="860" y="626" class="card-title">3C. On-Demand Distributed Clusters</text>
  <text x="860" y="642" class="card-mono">k8s/04 | Pluggable Workspace Tools</text>
  <text x="816" y="666" class="card-mono">• Ray 2.55.1 (ray2.55.1-py3.12-domino6.3 :8265)</text>
  <text x="816" y="684" class="card-mono">• Dask Cluster (dask-cluster-environment :8787)</text>
  <text x="816" y="702" class="card-mono">• Apache Spark On-Demand Executor Pods</text>
  <text x="816" y="720" class="card-mono">• MPI 4.1.4 (mpi-4.1.4-domino6.3 | UID 12574)</text>
  <text x="816" y="738" class="card-mono">• Hephaestus BuildKit Image Builder (70G Cache)</text>

  <!-- Card 3D -->
  <rect x="1180" y="602" width="368" height="156" rx="10" fill="#ffffff" stroke="#a7f3d0" stroke-width="1.5" filter="url(#shadow)"/>
  <image href="{icons['compute_engine']}" x="1192" y="616" width="38" height="38"/>
  <text x="1240" y="626" class="card-title">3D. Optional GPU Node Pool (gpu)</text>
  <text x="1240" y="642" class="card-mono">dominodatalab.com/node-pool=default-gpu</text>
  <text x="1196" y="666" class="card-body">• Machine: n1-highmem-8 / g2-standard-8</text>
  <text x="1196" y="684" class="card-mono">• GPU: nvidia-tesla-t4 / p100 / nvidia-l4</text>
  <text x="1196" y="702" class="card-mono">• Label: nvidia.com/gpu=true (400 GB Disk)</text>
  <text x="1196" y="720" class="card-mono">• Taint: nvidia.com/gpu=true:NoExecute</text>
  <text x="1196" y="738" class="card-mono">• Scale-to-Zero: min=0, max=2 per zone</text>

  <!-- ===================================================================== -->
  <!-- HORIZONTAL LAYER 4 (BOTTOM): STORAGE, ARTIFACT REGISTRY, WI & KMS     -->
  <!-- ===================================================================== -->
  <rect x="36" y="792" width="1528" height="214" rx="12" fill="#fef3c7" stroke="#f59e0b" stroke-width="2" filter="url(#shadow)"/>
  <rect x="36" y="792" width="1528" height="32" rx="10" fill="#d97706"/>
  <text x="54" y="813" class="badge">LAYER 4 (BOTTOM BAND) — PERSISTENT STORAGE, ARTIFACT REGISTRY, WORKLOAD IDENTITY &amp; CLOUD KMS CMEK (storage.tf | gcr.tf | kms.tf)</text>

  <!-- Card 4A -->
  <rect x="52" y="836" width="356" height="156" rx="10" fill="#ffffff" stroke="#fde68a" stroke-width="1.5" filter="url(#shadow)"/>
  <image href="{icons['filestore']}" x="64" y="850" width="38" height="38"/>
  <text x="112" y="860" class="card-title">4A. Block &amp; Shared StorageClasses</text>
  <text x="112" y="876" class="card-mono">dominodisk (RWO) &amp; dominoshared (RWX)</text>
  <text x="68" y="900" class="card-mono">• dominodisk: GCE PD (WaitForFirstConsumer)</text>
  <text x="68" y="918" class="card-mono">• dominoshared (Option 1): Filestore /share1 (1TB+)</text>
  <text x="68" y="936" class="card-mono">• dominoshared (Option 2): GCE NFS VM /srv/domino</text>
  <text x="68" y="954" class="card-mono">• dominoshared (Option 3): NetApp Volumes ONTAP</text>
  <text x="68" y="972" class="card-body">• Backs Domino Datasets, DFS &amp; Shared Blobs</text>

  <!-- Card 4B -->
  <rect x="424" y="836" width="360" height="156" rx="10" fill="#ffffff" stroke="#fde68a" stroke-width="1.5" filter="url(#shadow)"/>
  <image href="{icons['cloud_storage']}" x="436" y="850" width="38" height="38"/>
  <text x="484" y="860" class="card-title">4B. Cloud Storage Bucket (CMEK)</text>
  <text x="484" y="876" class="card-mono">dominodatalab-your-gcp-project-id-domino-gcp</text>
  <text x="440" y="900" class="card-body">• Regional Bucket (us-central1) + Versioning</text>
  <text x="440" y="918" class="card-mono">• uniform_bucket_level_access = true</text>
  <text x="440" y="936" class="card-mono">• public_access_prevention = "enforced"</text>
  <text x="440" y="954" class="card-mono">• Encrypted with Cloud KMS CryptoKey</text>
  <text x="440" y="972" class="card-body">• Backs blob_storage.backups.gcs &amp; Registry</text>

  <!-- Card 4C -->
  <rect x="800" y="836" width="364" height="156" rx="10" fill="#ffffff" stroke="#fde68a" stroke-width="1.5" filter="url(#shadow)"/>
  <image href="{icons['private_service_connect']}" x="812" y="850" width="38" height="38"/>
  <text x="860" y="860" class="card-title">4C. Google Artifact Registry (GAR)</text>
  <text x="860" y="876" class="card-mono">us-central1-docker.pkg.dev/.../domino-gcp-domino</text>
  <text x="816" y="900" class="card-body">• Format: DOCKER (immutable_tags = true)</text>
  <text x="816" y="918" class="card-body">• Stores Built Compute Environments &amp; Models</text>
  <text x="816" y="936" class="card-mono">• Builder SA: domino-gcp-gcr (repoAdmin)</text>
  <text x="816" y="954" class="card-mono">• Refresher SA: domino-gcp-gcr-cred (reader)</text>
  <text x="816" y="972" class="card-mono">• K8s SA: nucleus-gcr-credential-refresher</text>

  <!-- Card 4D -->
  <rect x="1180" y="836" width="368" height="156" rx="10" fill="#ffffff" stroke="#d97706" stroke-width="2" filter="url(#shadow)"/>
  <image href="{icons['key_management_service']}" x="1192" y="850" width="38" height="38"/>
  <text x="1240" y="860" class="card-title">4D. Cloud KMS &amp; Workload Identity</text>
  <text x="1240" y="876" class="card-mono">kms.tf &amp; service-accounts.tf</text>
  <text x="1196" y="900" class="card-mono">• KeyRing/Key: domino-gcp (86400s Rotation)</text>
  <text x="1196" y="918" class="card-mono">• Auto-Binds GKE Robot SA (123456789012)</text>
  <text x="1196" y="936" class="card-mono">• Auto-Binds GCS Project Service Agent</text>
  <text x="1196" y="954" class="card-mono">• WI Pool: your-gcp-project-id.svc.id.goog</text>
  <text x="1196" y="972" class="card-mono">• Binds nucleus, git, docker-registry, forge</text>

  <!-- Vertical Inter-Layer Arrows (Top-to-Bottom Flow) -->
  <path d="M 970 304 L 970 322" stroke="#1d4ed8" stroke-width="3" marker-end="url(#arrow-purple)"/>
  <path d="M 604 538 L 604 556" stroke="#7c3aed" stroke-width="3" marker-end="url(#arrow-green)"/>
  <path d="M 980 538 L 980 556" stroke="#7c3aed" stroke-width="3" marker-end="url(#arrow-green)"/>
  <path d="M 230 772 L 230 790" stroke="#059669" stroke-width="3" marker-end="url(#arrow-orange)"/>
  <path d="M 604 772 L 604 790" stroke="#059669" stroke-width="3" marker-end="url(#arrow-orange)"/>
  <path d="M 980 772 L 980 790" stroke="#059669" stroke-width="3" marker-end="url(#arrow-orange)"/>
  <path d="M 1364 772 L 1364 790" stroke="#059669" stroke-width="3" marker-end="url(#arrow-orange)"/>
</svg>
"""


def build_svg_2_network_and_wi_topology(icons: dict[str, str]) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 980" width="100%" height="100%">
  <defs>
    <style>
      .title {{ font: 700 22px 'Google Sans', 'Inter', 'Segoe UI', Arial, sans-serif; fill: #0f172a; }}
      .subtitle {{ font: 500 13px 'Google Sans', 'Inter', 'Segoe UI', Arial, sans-serif; fill: #475569; }}
      .card-title {{ font: 700 13px 'Google Sans', 'Inter', 'Segoe UI', Arial, sans-serif; fill: #0f172a; }}
      .card-body {{ font: 500 11px 'Google Sans', 'Inter', 'Segoe UI', Arial, sans-serif; fill: #334155; }}
      .card-mono {{ font: 600 10.2px 'Roboto Mono', monospace; fill: #0f172a; }}
      .badge {{ font: 700 10.8px 'Roboto Mono', monospace; fill: #ffffff; }}
    </style>
    <filter id="shadow" x="-2%" y="-4%" width="104%" height="110%">
      <feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#0f172a" flood-opacity="0.07"/>
    </filter>
    <marker id="arrow-blue" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#1d4ed8"/>
    </marker>
    <marker id="arrow-purple" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#7c3aed"/>
    </marker>
    <marker id="arrow-green" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#059669"/>
    </marker>
  </defs>

  <rect width="1600" height="980" rx="16" fill="#f8fafc" stroke="#cbd5e1" stroke-width="2"/>

  <!-- Top Header Banner -->
  <rect x="20" y="16" width="1560" height="64" rx="12" fill="#ffffff" stroke="#e2e8f0" stroke-width="1.5" filter="url(#shadow)"/>
  <rect x="20" y="16" width="10" height="64" rx="4" fill="#7c3aed"/>
  <text x="46" y="44" class="title">Domino 6.3 GKE Network Perimeter, Webhook Firewalls, Workload Identity &amp; KMS Security</text>
  <text x="46" y="65" class="subtitle">Horizontal Layered View: Public Edge &amp; IAP -&gt; VPC &amp; Master Peering Firewalls -&gt; Workload Identity Federation -&gt; Zero-Touch KMS IAM</text>

  <!-- ===================================================================== -->
  <!-- LAYER 1: PUBLIC EDGE, AUTHORIZED NETWORKS & IAP SSH                   -->
  <!-- ===================================================================== -->
  <rect x="36" y="100" width="1528" height="190" rx="12" fill="#eff6ff" stroke="#3b82f6" stroke-width="2" filter="url(#shadow)"/>
  <rect x="36" y="100" width="1528" height="32" rx="10" fill="#1d4ed8"/>
  <text x="54" y="121" class="badge">LAYER 1 — EXTERNAL ACCESS CONTROL, IAP TCP FORWARDING &amp; OUTBOUND NAT EGRESS (network.tf | node_pools.tf)</text>

  <rect x="52" y="144" width="484" height="132" rx="10" fill="#ffffff" stroke="#bfdbfe" stroke-width="1.5"/>
  <image href="{icons['cloud_load_balancing']}" x="66" y="158" width="38" height="38"/>
  <text x="116" y="168" class="card-title">1A. Master Authorized Networks &amp; HTTPS Ingress</text>
  <text x="116" y="184" class="card-mono">gke.public_access.enabled = true</text>
  <text x="68" y="208" class="card-body">• Restricts GKE API Server (6443) to Authorized CIDRs</text>
  <text x="68" y="226" class="card-body">• NGINX LoadBalancer Exposes Only TCP :80 and :443</text>
  <text x="68" y="244" class="card-mono">• Pod-Level Isolation via external-nginx NetworkPolicy</text>

  <rect x="558" y="144" width="484" height="132" rx="10" fill="#ffffff" stroke="#bfdbfe" stroke-width="1.5"/>
  <image href="{icons['identity_and_access_management']}" x="572" y="158" width="38" height="38"/>
  <text x="622" y="168" class="card-title">1B. Google Identity-Aware Proxy (IAP) SSH</text>
  <text x="622" y="184" class="card-mono">Firewall: domino-gcp-allow-ssh-from-iap</text>
  <text x="574" y="208" class="card-mono">• Source CIDR: 35.235.240.0/20 + var.allowed_ssh_ranges</text>
  <text x="574" y="226" class="card-mono">• Target Tag: domino-gcp-node-pool (TCP Port 22)</text>
  <text x="574" y="244" class="card-body">• Zero Public Node IPs Required for Node Debugging</text>

  <rect x="1064" y="144" width="484" height="132" rx="10" fill="#ffffff" stroke="#bfdbfe" stroke-width="1.5"/>
  <image href="{icons['cloud_nat']}" x="1078" y="158" width="38" height="38"/>
  <text x="1128" y="168" class="card-title">1C. Cloud Router &amp; Cloud NAT Egress</text>
  <text x="1128" y="184" class="card-mono">Router/NAT: domino-gcp (ALL_SUBNETWORKS)</text>
  <text x="1080" y="208" class="card-body">• Outbound Access for Private GKE Worker Nodes</text>
  <text x="1080" y="226" class="card-mono">• Pulls from: quay.io, domino.tech, gcr.io, docker.io</text>
  <text x="1080" y="244" class="card-mono">• Private Google Access Enabled on Subnet 10.138.0.0/20</text>

  <!-- ===================================================================== -->
  <!-- LAYER 2: VPC SUBNETTING & MASTER-TO-NODE WEBHOOK FIREWALLS            -->
  <!-- ===================================================================== -->
  <rect x="36" y="312" width="1528" height="196" rx="12" fill="#f5f3ff" stroke="#8b5cf6" stroke-width="2" filter="url(#shadow)"/>
  <rect x="36" y="312" width="1528" height="32" rx="10" fill="#7c3aed"/>
  <text x="54" y="333" class="badge">LAYER 2 — VPC SUBNETTING, CONTROL PLANE VPC PEERING &amp; ADMISSION WEBHOOK FIREWALLS (gke.tf | nfs-instance.tf)</text>

  <rect x="52" y="356" width="484" height="138" rx="10" fill="#ffffff" stroke="#ddd6fe" stroke-width="1.5"/>
  <image href="{icons['virtual_private_cloud']}" x="66" y="370" width="38" height="38"/>
  <text x="116" y="380" class="card-title">2A. Custom VPC &amp; Private Subnetwork</text>
  <text x="116" y="396" class="card-mono">Subnet: 10.138.0.0/20 (auto_create = false)</text>
  <text x="68" y="420" class="card-mono">• Secondary Range 1: GKE Pod IPv4 CIDR Block</text>
  <text x="68" y="438" class="card-mono">• Secondary Range 2: GKE Services IPv4 CIDR Block</text>
  <text x="68" y="456" class="card-mono">• Optional /24 VPC Peering for NetApp Volumes (GCNV)</text>
  <text x="68" y="474" class="card-mono">• Internal NFS Firewall: TCP/UDP 111 &amp; 2049</text>

  <rect x="558" y="356" width="990" height="138" rx="10" fill="#ffffff" stroke="#7c3aed" stroke-width="2"/>
  <image href="{icons['google_kubernetes_engine']}" x="572" y="370" width="38" height="38"/>
  <text x="622" y="380" class="card-title">2B. GKE Master Control Plane Webhook Firewall (domino-gcp-gke-master-webhooks)</text>
  <text x="622" y="396" class="card-mono">Source: 172.16.1.0/28 (GKE Master Peering) -&gt; Target Tag: domino-gcp</text>
  <text x="574" y="422" class="card-mono">• TCP 6443  : Kubernetes API &amp; Custom Resource Conversion Webhooks</text>
  <text x="574" y="440" class="card-mono">• TCP 8080  : Internal HTTP Webhook Endpoints</text>
  <text x="574" y="458" class="card-mono">• TCP 8443  : NGINX Ingress Controller Validating Admission Webhook</text>
  <text x="1080" y="422" class="card-mono">• TCP 9443  : Cert-Manager &amp; Domino Platform Operator Webhooks</text>
  <text x="1080" y="440" class="card-mono">• TCP 10250 : Kubelet API (kubectl exec, logs &amp; metrics-server)</text>
  <text x="1080" y="458" class="card-mono">• TCP 15017 : Istio Sidecar Injector / Mutating Webhook</text>

  <!-- ===================================================================== -->
  <!-- LAYER 3: GKE WORKLOAD IDENTITY FEDERATION                             -->
  <!-- ===================================================================== -->
  <rect x="36" y="530" width="1528" height="206" rx="12" fill="#ecfdf5" stroke="#10b981" stroke-width="2" filter="url(#shadow)"/>
  <rect x="36" y="530" width="1528" height="32" rx="10" fill="#059669"/>
  <text x="54" y="551" class="badge">LAYER 3 — GKE WORKLOAD IDENTITY FEDERATION: KUBERNETES SAs &lt;-&gt; GCP IAM SERVICE ACCOUNTS (service-accounts.tf | gcr.tf)</text>

  <rect x="52" y="574" width="484" height="148" rx="10" fill="#ffffff" stroke="#a7f3d0" stroke-width="1.5"/>
  <image href="{icons['identity_and_access_management']}" x="66" y="588" width="38" height="38"/>
  <text x="116" y="598" class="card-title">3A. Domino Platform Service Account</text>
  <text x="116" y="614" class="card-mono">GCP SA: domino-gcp-platform@your-gcp-project-id...</text>
  <text x="68" y="638" class="card-mono">• Roles: storage.objectAdmin (on GCS Bucket)</text>
  <text x="68" y="656" class="card-mono">• Roles: logging.logWriter, monitoring.metricWriter</text>
  <text x="68" y="674" class="card-body">• Bound via roles/iam.workloadIdentityUser to K8s SAs:</text>
  <text x="68" y="692" class="card-mono">  domino-platform/{{nucleus, git, docker-registry,</text>
  <text x="68" y="708" class="card-mono">  domino-data-importer}}</text>

  <rect x="558" y="574" width="484" height="148" rx="10" fill="#ffffff" stroke="#a7f3d0" stroke-width="1.5"/>
  <image href="{icons['identity_and_access_management']}" x="572" y="588" width="38" height="38"/>
  <text x="622" y="598" class="card-title">3B. Environment Builder Service Account</text>
  <text x="622" y="614" class="card-mono">GCP SA: domino-gcp-gcr@your-gcp-project-id...</text>
  <text x="574" y="638" class="card-mono">• Roles: artifactregistry.repoAdmin (on GAR repo)</text>
  <text x="574" y="656" class="card-mono">• Roles: storage.admin (for registry layer blobs)</text>
  <text x="574" y="674" class="card-body">• Bound via roles/iam.workloadIdentityUser to K8s SAs:</text>
  <text x="574" y="692" class="card-mono">  domino-compute/hephaestus</text>
  <text x="574" y="708" class="card-mono">  domino-compute/forge</text>

  <rect x="1064" y="574" width="484" height="148" rx="10" fill="#ffffff" stroke="#a7f3d0" stroke-width="1.5"/>
  <image href="{icons['identity_and_access_management']}" x="1078" y="588" width="38" height="38"/>
  <text x="1128" y="598" class="card-title">3C. GCR Credential Refresher &amp; Node Pool SAs</text>
  <text x="1128" y="614" class="card-mono">GCP SAs: domino-gcp-gcr-cred &amp; domino-gcp-gke</text>
  <text x="1080" y="638" class="card-mono">• domino-gcp-gcr-cred: artifactregistry.reader +</text>
  <text x="1080" y="656" class="card-mono">  iam.serviceAccountTokenCreator</text>
  <text x="1080" y="674" class="card-mono">• K8s SA: domino-platform/nucleus-gcr-credential-refresher</text>
  <text x="1080" y="692" class="card-mono">• domino-gcp-gke: Node Pool VM SA (artifactregistry.reader,</text>
  <text x="1080" y="708" class="card-mono">  storage.objectViewer, logging, monitoring)</text>

  <!-- ===================================================================== -->
  <!-- LAYER 4: AUTOMATED CLOUD KMS CMEK ENCRYPTION                          -->
  <!-- ===================================================================== -->
  <rect x="36" y="758" width="1528" height="196" rx="12" fill="#fef3c7" stroke="#f59e0b" stroke-width="2" filter="url(#shadow)"/>
  <rect x="36" y="758" width="1528" height="32" rx="10" fill="#d97706"/>
  <text x="54" y="779" class="badge">LAYER 4 — ZERO-TOUCH CLOUD KMS CMEK ENCRYPTION FOR GKE SECRETS &amp; GCS BACKUPS (apis.tf | kms.tf)</text>

  <rect x="52" y="802" width="736" height="136" rx="10" fill="#ffffff" stroke="#d97706" stroke-width="2"/>
  <image href="{icons['key_management_service']}" x="66" y="816" width="38" height="38"/>
  <text x="116" y="826" class="card-title">4A. Cloud KMS KeyRing &amp; CryptoKey (86,400s Daily Rotation)</text>
  <text x="116" y="842" class="card-mono">projects/your-gcp-project-id/locations/us-central1/keyRings/domino-gcp/cryptoKeys/domino-gcp</text>
  <text x="68" y="868" class="card-body">• Purpose: ENCRYPT_DECRYPT  |  Automatic Daily Key Rotation (rotation_period = "86400s")</text>
  <text x="68" y="886" class="card-body">• Encrypts Kubernetes Secrets at rest in GKE Control Plane etcd (database_encryption = ENCRYPTED)</text>
  <text x="68" y="904" class="card-body">• Encrypts all Domino Backups &amp; Registry Blobs in GCS (default_kms_key_name)</text>

  <rect x="812" y="802" width="736" height="136" rx="10" fill="#ffffff" stroke="#fde68a" stroke-width="1.5"/>
  <image href="{icons['secret_manager']}" x="826" y="816" width="38" height="38"/>
  <text x="876" y="826" class="card-title">4B. Automated Service Agent KMS IAM Binding (Eliminates Manual Console Step)</text>
  <text x="876" y="842" class="card-mono">Role: roles/cloudkms.cryptoKeyEncrypterDecrypter</text>
  <text x="828" y="868" class="card-mono">• Principal 1: service-123456789012@container-engine-robot.iam.gserviceaccount.com (GKE Agent)</text>
  <text x="828" y="886" class="card-mono">• Principal 2: service-123456789012@gs-project-accounts.iam.gserviceaccount.com (GCS Agent)</text>
  <text x="828" y="904" class="card-body">• Enforced via depends_on before google_container_cluster and google_storage_bucket creation</text>

  <path d="M 800 290 L 800 310" stroke="#1d4ed8" stroke-width="3" marker-end="url(#arrow-purple)"/>
  <path d="M 800 508 L 800 528" stroke="#7c3aed" stroke-width="3" marker-end="url(#arrow-green)"/>
  <path d="M 800 736 L 800 756" stroke="#059669" stroke-width="3" marker-end="url(#arrow-blue)"/>
</svg>
"""


def build_svg_3_deployment_and_nexus_lifecycle(icons: dict[str, str]) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 980" width="100%" height="100%">
  <defs>
    <style>
      .title {{ font: 700 22px 'Google Sans', 'Inter', 'Segoe UI', Arial, sans-serif; fill: #0f172a; }}
      .subtitle {{ font: 500 13px 'Google Sans', 'Inter', 'Segoe UI', Arial, sans-serif; fill: #475569; }}
      .card-title {{ font: 700 13px 'Google Sans', 'Inter', 'Segoe UI', Arial, sans-serif; fill: #0f172a; }}
      .card-body {{ font: 500 11px 'Google Sans', 'Inter', 'Segoe UI', Arial, sans-serif; fill: #334155; }}
      .card-mono {{ font: 600 10.2px 'Roboto Mono', monospace; fill: #0f172a; }}
      .badge {{ font: 700 10.8px 'Roboto Mono', monospace; fill: #ffffff; }}
    </style>
    <filter id="shadow" x="-2%" y="-4%" width="104%" height="110%">
      <feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#0f172a" flood-opacity="0.07"/>
    </filter>
    <marker id="arrow-blue" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#1d4ed8"/>
    </marker>
    <marker id="arrow-purple" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#7c3aed"/>
    </marker>
    <marker id="arrow-green" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#059669"/>
    </marker>
  </defs>

  <rect width="1600" height="980" rx="16" fill="#f8fafc" stroke="#cbd5e1" stroke-width="2"/>

  <!-- Top Header Banner -->
  <rect x="20" y="16" width="1560" height="64" rx="12" fill="#ffffff" stroke="#e2e8f0" stroke-width="1.5" filter="url(#shadow)"/>
  <rect x="20" y="16" width="10" height="64" rx="4" fill="#059669"/>
  <text x="46" y="44" class="title">Domino 6.3 Deployment Pipeline, Operator Drift Reconciliation, Keycloak SSO &amp; Day-2 Lifecycle</text>
  <text x="46" y="65" class="subtitle">Horizontal Layered View: Phase 1 Terraform IaC -&gt; Phase 2 Platform Operator (ddlctl v0.6.4) -&gt; Keycloak &amp; UAT -&gt; Day-2 Upgrades &amp; Nexus</text>

  <!-- ===================================================================== -->
  <!-- LAYER 1: PHASE 1 — TERRAFORM INFRASTRUCTURE & CONFIG RENDERING        -->
  <!-- ===================================================================== -->
  <rect x="36" y="100" width="1528" height="190" rx="12" fill="#eff6ff" stroke="#3b82f6" stroke-width="2" filter="url(#shadow)"/>
  <rect x="36" y="100" width="1528" height="32" rx="10" fill="#1d4ed8"/>
  <text x="54" y="121" class="badge">LAYER 1 — PHASE 1: TERRAFORM GCP INFRASTRUCTURE PROVISIONING &amp; AUTO-RENDERED DOMINO.YML (scripts/01 &amp; 02)</text>

  <rect x="52" y="144" width="484" height="132" rx="10" fill="#ffffff" stroke="#bfdbfe" stroke-width="1.5"/>
  <image href="{icons['compute_engine']}" x="66" y="158" width="38" height="38"/>
  <text x="116" y="168" class="card-title">1A. Prerequisite &amp; Quota Validation</text>
  <text x="116" y="184" class="card-mono">scripts/01_check_prerequisites.sh</text>
  <text x="68" y="208" class="card-mono">• Verifies gcloud, terraform 1.9+, kubectl, helm</text>
  <text x="68" y="226" class="card-mono">• Installs ddlctl v0.6.4 &amp; checks Docker socket</text>
  <text x="68" y="244" class="card-mono">• Verifies your-gcp-project-id N2 CPU &amp; VPC Quotas</text>

  <rect x="558" y="144" width="484" height="132" rx="10" fill="#ffffff" stroke="#bfdbfe" stroke-width="1.5"/>
  <image href="{icons['google_kubernetes_engine']}" x="572" y="158" width="38" height="38"/>
  <text x="622" y="168" class="card-title">1B. Terraform Apply (58 GCP Resources)</text>
  <text x="622" y="184" class="card-mono">scripts/02_provision_gcp_infra.sh --apply</text>
  <text x="574" y="208" class="card-body">• Enables 13 GCP APIs including file.googleapis.com</text>
  <text x="574" y="226" class="card-body">• Creates KMS Key, VPC, GKE 1.35 &amp; 3 Node Pools</text>
  <text x="574" y="244" class="card-body">• Creates Filestore (1TB), CMEK GCS &amp; GAR Repo</text>

  <rect x="1064" y="144" width="484" height="132" rx="10" fill="#ffffff" stroke="#2563eb" stroke-width="2"/>
  <image href="{icons['cloud_storage']}" x="1078" y="158" width="38" height="38"/>
  <text x="1128" y="168" class="card-title">1C. Automated domino.yml Generation</text>
  <text x="1128" y="184" class="card-mono">domino-config.tf -&gt; generated/domino.yml</text>
  <text x="1080" y="208" class="card-mono">• Maps all 19 ddlcloud_generator_gke outputs</text>
  <text x="1080" y="226" class="card-mono">• Populates Filestore IP, GCS Bucket, GAR &amp; SAs</text>
  <text x="1080" y="244" class="card-mono">• Supports Standard (300) &amp; Large (600) Profiles</text>

  <!-- ===================================================================== -->
  <!-- LAYER 2: PHASE 2 — PLATFORM OPERATOR & HELMRELEASE RECONCILIATION     -->
  <!-- ===================================================================== -->
  <rect x="36" y="312" width="1528" height="196" rx="12" fill="#f5f3ff" stroke="#8b5cf6" stroke-width="2" filter="url(#shadow)"/>
  <rect x="36" y="312" width="1528" height="32" rx="10" fill="#7c3aed"/>
  <text x="54" y="333" class="badge">LAYER 2 — PHASE 2: DOMINO PLATFORM OPERATOR BOOTSTRAP, DOMINO CRD &amp; DRIFT RECONCILIATION (scripts/03)</text>

  <rect x="52" y="356" width="484" height="138" rx="10" fill="#ffffff" stroke="#ddd6fe" stroke-width="1.5"/>
  <image href="{icons['secret_manager']}" x="66" y="370" width="38" height="38"/>
  <text x="116" y="380" class="card-title">2A. K8s Namespaces, TLS &amp; NetworkPolicies</text>
  <text x="116" y="396" class="card-mono">k8s/01..04 YAML Manifests</text>
  <text x="68" y="420" class="card-mono">• Namespaces: domino-platform, compute, system</text>
  <text x="68" y="438" class="card-mono">• TLS Secret: domino-platform/my-cert</text>
  <text x="68" y="456" class="card-mono">• NetworkPolicy: external-nginx (Ingress)</text>
  <text x="68" y="474" class="card-mono">• ConfigMap: default/domino-custom-certificates</text>

  <rect x="558" y="356" width="484" height="138" rx="10" fill="#ffffff" stroke="#7c3aed" stroke-width="2"/>
  <image href="{icons['google_kubernetes_engine']}" x="572" y="370" width="38" height="38"/>
  <text x="622" y="380" class="card-title">2B. Platform Operator &amp; Domino CRD</text>
  <text x="622" y="396" class="card-mono">ddlctl v0.6.4 | Agent 6.3.0.catalog-1df6e73</text>
  <text x="574" y="420" class="card-mono">1. ddlctl bootstrap --skip-domino-resource</text>
  <text x="574" y="438" class="card-mono">2. ddlctl create config --preset gke</text>
  <text x="574" y="456" class="card-mono">3. ddlctl create domino --config domino.yml</text>
  <text x="574" y="474" class="card-body">• Offline Option: ddlctl images + skopeo copy</text>

  <rect x="1064" y="356" width="484" height="138" rx="10" fill="#ffffff" stroke="#ddd6fe" stroke-width="1.5"/>
  <image href="{icons['google_kubernetes_engine']}" x="1078" y="370" width="38" height="38"/>
  <text x="1128" y="380" class="card-title">2C. 5-Minute HelmRelease Drift Loop</text>
  <text x="1128" y="396" class="card-mono">CRD: helmreleases.helm.toolkit.fluxcd.io</text>
  <text x="1080" y="420" class="card-mono">• Inspect: ddlctl get helmrelease --all</text>
  <text x="1080" y="438" class="card-mono">• Stalled: ddlctl get helmrelease -A --status stalled=true</text>
  <text x="1080" y="456" class="card-mono">• Diff   : ddlctl diff helmrelease &lt;name&gt;</text>
  <text x="1080" y="474" class="card-mono">• Repair : ddlctl reconcile helmrelease --reset --force</text>

  <!-- ===================================================================== -->
  <!-- LAYER 3: KEYCLOAK AUTHENTICATION & USER ACCEPTANCE TESTING (UAT)      -->
  <!-- ===================================================================== -->
  <rect x="36" y="530" width="1528" height="196" rx="12" fill="#ecfdf5" stroke="#10b981" stroke-width="2" filter="url(#shadow)"/>
  <rect x="36" y="530" width="1528" height="32" rx="10" fill="#059669"/>
  <text x="54" y="551" class="badge">LAYER 3 — KEYCLOAK IDENTITY ONBOARDING (DOMINOREALM), SSO FEDERATION &amp; USER ACCEPTANCE TESTING (UAT)</text>

  <rect x="52" y="574" width="736" height="138" rx="10" fill="#ffffff" stroke="#a7f3d0" stroke-width="1.5"/>
  <image href="{icons['identity_and_access_management']}" x="66" y="588" width="38" height="38"/>
  <text x="116" y="598" class="card-title">3A. Keycloak Authentication Setup (https://&lt;DOMINO_URL&gt;/auth/)</text>
  <text x="116" y="614" class="card-mono">Secret: domino-platform/keycloak-http | Realm: DominoRealm</text>
  <text x="68" y="638" class="card-body">• Option 1 (Self-Signup): Enable 'User Registration' under Realm Settings -&gt; Login, register first user, then disable</text>
  <text x="68" y="656" class="card-body">• Option 2 (Admin Provisioned): Manage -&gt; Users -&gt; Add User -&gt; Credentials -&gt; Role Mappings -&gt; Client Roles: domino-play -&gt; User</text>
  <text x="68" y="674" class="card-body">• Configure Realm Settings -&gt; Email (SMTP) &amp; Identity Providers (OIDC / SAML 2.0 / LDAP Federation)</text>
  <text x="68" y="692" class="card-mono">• Promote Admin in Domino UI: Admin -&gt; Advanced -&gt; Users</text>

  <rect x="812" y="574" width="736" height="138" rx="10" fill="#ffffff" stroke="#059669" stroke-width="2"/>
  <image href="{icons['google_kubernetes_engine']}" x="826" y="588" width="38" height="38"/>
  <text x="876" y="598" class="card-title">3B. Comprehensive User Acceptance Testing (UAT) Verification Suite</text>
  <text x="876" y="614" class="card-mono">https://docs.domino.ai/6.3/admin/installation/user-acceptance-testing</text>
  <text x="828" y="638" class="card-body">• Admin &amp; Control Center: Verify active Platform &amp; Compute nodes, Central Config, and Executions view</text>
  <text x="828" y="656" class="card-body">• Compute Environments: Build custom environment via Hephaestus &amp; verify image push to Google Artifact Registry</text>
  <text x="828" y="674" class="card-body">• Workspaces &amp; Jobs: Launch JupyterLab, RStudio, VSCode; run batch Python/R jobs; verify DFS &amp; Git sync</text>
  <text x="828" y="692" class="card-body">• Datasets, Apps &amp; Clusters: Test ReadWriteMany Dataset snapshots, Flask/Shiny Apps, Model APIs &amp; Ray/Dask/Spark</text>

  <!-- ===================================================================== -->
  <!-- LAYER 4: DAY-2 GKE/DOMINO UPGRADES & NEXUS HYBRID DATA PLANES         -->
  <!-- ===================================================================== -->
  <rect x="36" y="748" width="1528" height="206" rx="12" fill="#fef3c7" stroke="#f59e0b" stroke-width="2" filter="url(#shadow)"/>
  <rect x="36" y="748" width="1528" height="32" rx="10" fill="#d97706"/>
  <text x="54" y="769" class="badge">LAYER 4 — DAY-2 OPERATIONS: GKE KUBERNETES UPGRADE, DOMINO UPGRADE &amp; NEXUS REMOTE DATA PLANES (scripts/04)</text>

  <rect x="52" y="792" width="484" height="146" rx="10" fill="#ffffff" stroke="#fde68a" stroke-width="1.5"/>
  <image href="{icons['google_kubernetes_engine']}" x="66" y="806" width="38" height="38"/>
  <text x="116" y="816" class="card-title">4A. GKE Cluster &amp; Node Pool Upgrade</text>
  <text x="116" y="832" class="card-mono">scripts/04_upgrade_gke_cluster.sh</text>
  <text x="68" y="856" class="card-mono">1. Backup &amp; delete MongoDB PDBs in domino-platform:</text>
  <text x="68" y="874" class="card-mono">   mongodb-arbiter, mongodb-primary, mongodb-secondary</text>
  <text x="68" y="892" class="card-mono">2. Upgrade GKE Control Plane (--master)</text>
  <text x="68" y="910" class="card-mono">3. Upgrade platform, compute, gpu Node Pools</text>
  <text x="68" y="928" class="card-mono">4. Restore MongoDB PodDisruptionBudgets</text>

  <rect x="558" y="792" width="484" height="146" rx="10" fill="#ffffff" stroke="#fde68a" stroke-width="1.5"/>
  <image href="{icons['compute_engine']}" x="572" y="806" width="38" height="38"/>
  <text x="622" y="816" class="card-title">4B. Domino Platform Version Upgrade</text>
  <text x="622" y="832" class="card-mono">ddlctl upgrade domino</text>
  <text x="574" y="856" class="card-body">1. Run Domino Admin Toolkit cluster health checks</text>
  <text x="574" y="874" class="card-mono">2. Check drift: ddlctl get helmrelease -A --status stalled=true</text>
  <text x="574" y="892" class="card-mono">3. Dry-Run: spec.agent.spec.dryRunMode = "true"</text>
  <text x="574" y="910" class="card-mono">4. Upgrade: ddlctl upgrade domino --agent-version &lt;TAG&gt;</text>
  <text x="574" y="928" class="card-body">• Migrates .spec.config schema automatically</text>

  <rect x="1064" y="792" width="484" height="146" rx="10" fill="#ffffff" stroke="#d97706" stroke-width="2"/>
  <image href="{icons['private_service_connect']}" x="1078" y="806" width="38" height="38"/>
  <text x="1128" y="816" class="card-title">4C. Domino Nexus Hybrid Data Planes</text>
  <text x="1128" y="832" class="card-mono">generated/domino-nexus-dataplane.yml</text>
  <text x="1080" y="856" class="card-mono">• Preset: ddlctl create config --preset data-plane</text>
  <text x="1080" y="874" class="card-mono">• Config: control_plane: false, data_plane.type: remote</text>
  <text x="1080" y="892" class="card-body">• Connects to Control Plane LBs: RabbitMQ (5672/5552),</text>
  <text x="1080" y="910" class="card-body">  Vault (8200), Docker Registry (443) &amp; Domino API (443)</text>
  <text x="1080" y="928" class="card-body">• Direct Browser-to-Data-Plane Workspace Routing</text>

  <path d="M 800 290 L 800 310" stroke="#1d4ed8" stroke-width="3" marker-end="url(#arrow-purple)"/>
  <path d="M 800 508 L 800 528" stroke="#7c3aed" stroke-width="3" marker-end="url(#arrow-green)"/>
  <path d="M 800 726 L 800 746" stroke="#059669" stroke-width="3" marker-end="url(#arrow-blue)"/>
</svg>
"""


def main() -> None:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    icon_names = [
        "cloud_storage",
        "compute_engine",
        "virtual_private_cloud",
        "identity_and_access_management",
        "private_service_connect",
        "cloud_nat",
        "key_management_service",
        "secret_manager",
        "cloud_load_balancing",
        "filestore",
        "google_kubernetes_engine",
        "cloud_dns",
        "cloud_armor",
    ]
    icons = {name: load_icon_data_uri(name) for name in icon_names}

    svg1 = ASSETS_DIR / "01_domino_gcp_reference_architecture.svg"
    svg2 = ASSETS_DIR / "02_domino_network_and_workload_identity_topology.svg"
    svg3 = ASSETS_DIR / "03_domino_deployment_and_nexus_lifecycle.svg"

    svg1.write_text(build_svg_1_reference_architecture(icons), encoding="utf-8")
    svg2.write_text(build_svg_2_network_and_wi_topology(icons), encoding="utf-8")
    svg3.write_text(build_svg_3_deployment_and_nexus_lifecycle(icons), encoding="utf-8")
    print("Generated 3 HORIZONTAL-LAYERED SVG blueprints in", ASSETS_DIR)

    chrome_bin = shutil.which("google-chrome") or "/usr/bin/google-chrome"
    if pathlib.Path(chrome_bin).exists():
        specs = [
            (svg1, "1600,1040"),
            (svg2, "1600,980"),
            (svg3, "1600,980"),
        ]
        for svg_path, win_size in specs:
            png_path = svg_path.with_suffix(".png")
            subprocess.run(
                [
                    chrome_bin,
                    "--headless",
                    "--disable-gpu",
                    "--no-sandbox",
                    "--hide-scrollbars",
                    f"--window-size={win_size}",
                    f"--screenshot={png_path}",
                    f"file://{svg_path}",
                ],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        print("Rendered 3 HORIZONTAL-LAYERED PNG blueprints in", ASSETS_DIR)


if __name__ == "__main__":
    main()
