# Domino Data Lab 6.3 on Google Cloud Platform (GKE 1.35) — Terraform IaC & Deployment Suite

[![Domino 6.3.0](https://img.shields.io/badge/Domino_Data_Lab-6.3.0-2563eb?style=for-the-badge)](https://docs.domino.ai/6.3/admin/installation/manage-deployments/gcp/index)
[![GKE 1.35](https://img.shields.io/badge/Google_Kubernetes_Engine-1.35_STABLE-4285F4?style=for-the-badge&logo=googlekubernetesengine&logoColor=white)](https://cloud.google.com/kubernetes-engine)
[![Terraform 1.9+](https://img.shields.io/badge/Terraform-%3E%3D_1.4-7B42BC?style=for-the-badge&logo=terraform&logoColor=white)](https://github.com/dominodatalab/terraform-gcp-gke)
[![ddlctl 0.6.4](https://img.shields.io/badge/ddlctl-0.6.4-059669?style=for-the-badge)](https://docs.domino.ai/6.3/admin/installation/releases)

Production-grade **Terraform Infrastructure-as-Code (IaC)**, **Kubernetes Manifests**, and **Automated Deployment Scripts** for provisioning **Domino Data Lab 6.3.0** (`fleetcommand-agent: 6.3.0.catalog-1df6e73`, `ddlctl: 0.6.4`) on **Google Kubernetes Engine (GKE 1.35)** in GCP project **`your-gcp-project-id`**.

---

## 1. End-to-End Reference Architecture (Horizontal Layered View)

![Domino Data Lab 6.3 on GCP Reference Architecture](assets/01_domino_gcp_reference_architecture.svg)

```mermaid
flowchart TB
    classDef layer1 fill:#eff6ff,stroke:#2563eb,stroke-width:2px,color:#1e3a8a
    classDef layer2 fill:#f5f3ff,stroke:#7c3aed,stroke-width:2px,color:#4c1d95
    classDef layer3 fill:#ecfdf5,stroke:#059669,stroke-width:2px,color:#064e3b
    classDef layer4 fill:#fef3c7,stroke:#d97706,stroke-width:2px,color:#78350f

    subgraph L1["Layer 1 (Top Band): External HTTPS Ingress, Cloud DNS & TLS Termination"]
        direction LR
        USERS["Data Scientists & Admins<br/>Browser / Domino CLI / REST APIs"]:::layer1
        DNS["Cloud DNS & Static IPv4<br/>domino.<domain> (A + CAA)"]:::layer1
        GLB["External HTTPS Load Balancer<br/>TCP 80/443 | WebSockets | /healthz"]:::layer1
        NGINX["NGINX Ingress Controller<br/>Secret: domino-platform/my-cert<br/>NetworkPolicy: external-nginx"]:::layer1
        USERS --> DNS --> GLB --> NGINX
    end

    subgraph L2["Layer 2 (Second Band): GKE 1.35 Control Plane & Domino Platform Tier (domino-platform & domino-system)"]
        direction LR
        GKE_CP["Private Regional GKE 1.35 Control Plane<br/>Master CIDR: 172.16.1.0/28 | VPA + Dataplane V2<br/>Webhooks: 6443, 8080, 8443, 9443, 10250, 15017"]:::layer2
        OP["Domino Platform Operator (domino-operator)<br/>ddlctl v0.6.4 | Agent 6.3.0.catalog-1df6e73<br/>5-Min HelmRelease Drift Reconciliation"]:::layer2
        PLAT_POOL["Platform Node Pool (platform)<br/>Standard: 4x n2-highmem-8 (300 Execs)<br/>Large: 5x n2-highmem-16 (600 Execs)"]:::layer2
        PLAT_SVCS["Platform Microservices<br/>• Nucleus UI/API & Keycloak (/auth/)<br/>• MongoDB ReplicaSet + PostgreSQL + Vault<br/>• RabbitMQ + Git + MLflow + GCR Refresher"]:::layer2
        GKE_CP --- OP --> PLAT_POOL --- PLAT_SVCS
    end

    subgraph L3["Layer 3 (Third Band): Elastic Compute Grid, Distributed HPC Clusters & Build Tier (domino-compute)"]
        direction LR
        COMP_POOL["Compute Node Pool (compute)<br/>n2-highmem-8 (8 vCPU, 64GB RAM, 400GB Disk)<br/>GCFS Image Streaming | domino/build-node=true"]:::layer3
        WORKLOADS["User Execution Pods<br/>• JupyterLab, Jupyter, RStudio, VS Code<br/>• Batch Jobs, Flask/Shiny Apps & Model APIs"]:::layer3
        CLUSTERS["Distributed Compute & Image Builders<br/>• Ray 2.55.1 (:8265) | Dask (:8787) | Spark | MPI 4.1.4<br/>• Hephaestus BuildKit Image Builder"]:::layer3
        GPU_POOL["Optional GPU Node Pool (gpu)<br/>n1-highmem-8 / g2-standard-8 (T4 / P100 / L4)<br/>Taint: nvidia.com/gpu=true:NoExecute"]:::layer3
        COMP_POOL --- WORKLOADS & CLUSTERS
        GPU_POOL --- WORKLOADS
    end

    subgraph L4["Layer 4 (Bottom Band): Shared Storage, Artifact Registry, Workload Identity & Cloud KMS CMEK"]
        direction LR
        BLOCK["Block Storage (dominodisk)<br/>GCE Persistent Disk (RWO)<br/>WaitForFirstConsumer"]:::layer4
        SHARED["Shared Storage (dominoshared)<br/>Cloud Filestore /share1 (1TB+)<br/>or GCE NFS VM / NetApp Volumes (RWX)"]:::layer4
        GCS["Cloud Storage Bucket (CMEK)<br/>dominodatalab-your-gcp-project-id-domino-gcp<br/>Backups & Registry Blobs"]:::layer4
        GAR_KMS["Artifact Registry & Cloud KMS<br/>• GAR: domino-gcp-domino (Immutable Tags)<br/>• KMS Key (86400s Rotation) + Auto IAM"]:::layer4
    end

    L1 --> L2
    L2 --> L3
    L2 --> L4
    L3 --> L4
```

---

## 2. Network Perimeter, Workload Identity & Zero-Touch KMS Security

![Domino 6.3 Network Perimeter, Workload Identity and KMS Topology](assets/02_domino_network_and_workload_identity_topology.svg)

| Security & Network Domain | Terraform Resource | Configuration Details |
| :--- | :--- | :--- |
| **VPC & Subnet** | `google_compute_network` / `subnetwork` | Custom VPC `domino-gcp`, Subnet `10.138.0.0/20`, `private_ip_google_access = true`, Cloud Router & Cloud NAT |
| **GKE Control Plane Webhooks** | `google_compute_firewall.master_webhooks` | Permits GKE Master (`172.16.1.0/28`) $\rightarrow$ Worker Nodes on TCP `6443`, `8080`, `8443`, `9443`, `10250`, `15017` |
| **IAP SSH Tunneling** | `google_compute_firewall.iap_tcp_forwarding` | Permits Google IAP (`35.235.240.0/20`) $\rightarrow$ `domino-gcp-node-pool` on TCP `22` (Zero public node IPs) |
| **Zero-Touch KMS CMEK** | `google_kms_crypto_key_iam_binding` | Auto-binds `roles/cloudkms.cryptoKeyEncrypterDecrypter` to both `service-123456789012@container-engine-robot.iam.gserviceaccount.com` and `service-123456789012@gs-project-accounts.iam.gserviceaccount.com` |
| **Platform Workload Identity** | `domino-gcp-platform` SA | Bound to `domino-platform/{nucleus, git, docker-registry, domino-data-importer}` (`roles/storage.objectAdmin`) |
| **Builder Workload Identity** | `domino-gcp-gcr` SA | Bound to `domino-compute/{hephaestus, forge}` (`roles/artifactregistry.repoAdmin`, `roles/storage.admin`) |
| **Credential Refresher WI** | `domino-gcp-gcr-cred` SA | Bound to `domino-platform/nucleus-gcr-credential-refresher` (`roles/artifactregistry.reader`, `serviceAccountTokenCreator`) |

---

## 3. Two-Phase Deployment Pipeline, Drift Loop & Day-2 Operations

![Domino 6.3 Deployment Pipeline and Day-2 Lifecycle](assets/03_domino_deployment_and_nexus_lifecycle.svg)

```mermaid
sequenceDiagram
    autonumber
    actor Admin as Platform Engineer
    participant TF as Terraform (terraform/)
    participant GCP as GCP (your-gcp-project-id)
    participant K8S as GKE 1.35 Cluster
    participant OP as Domino Operator (ddlctl v0.6.4)
    participant KC as Keycloak (/auth/ DominoRealm)

    Admin->>TF: ./scripts/02_provision_gcp_infra.sh --apply
    TF->>GCP: Enable 13 APIs + Create KMS Key & Bind GKE/GCS Service Agents
    TF->>GCP: Provision VPC, Private GKE 1.35, Node Pools (platform, compute, gpu)
    TF->>GCP: Provision Cloud Filestore (1TB /share1), CMEK GCS Bucket & GAR Repo
    TF-->>Admin: Render generated/domino.yml (Schema 1.16) + terraform-outputs.json

    Admin->>K8S: ./scripts/03_deploy_domino_platform.sh
    K8S->>K8S: Apply Namespaces, dominodisk StorageClass, TLS Secret (my-cert) & external-nginx NetworkPolicy
    Admin->>OP: ddlctl bootstrap --skip-domino-resource
    Admin->>OP: ddlctl create domino --config generated/domino.yml --agent-version 6.3.0.catalog-1df6e73
    OP->>K8S: Reconcile HelmReleases (5-min drift loop) & Expose NGINX LoadBalancer
    Admin->>KC: Login with keycloak-http secret -> Configure DominoRealm & Assign domino-play User role
```

---

## 4. Quick-Start Deployment Commands

```bash
# Step 1: Validate CLI tools (gcloud, terraform, kubectl, helm, ddlctl v0.6.4) & GCP quotas
./scripts/01_check_prerequisites.sh

# Step 2: Provision GKE 1.35, Cloud Filestore, CMEK GCS, GAR & render generated/domino.yml
./scripts/02_provision_gcp_infra.sh --apply

# Step 3: Configure GKE namespaces, TLS secret (domino-platform/my-cert), NetworkPolicies & Domino Operator
./scripts/03_deploy_domino_platform.sh

# Step 4: Run the 55-check automated verification suite
python3 ./tests/validate_all.py
```

---

## 5. Live Provisioned Environment (`your-gcp-project-id`)

| Resource Category | Live GCP Resource ID / Value | Status |
| :--- | :--- | :--- |
| **GKE Cluster** | `projects/your-gcp-project-id/locations/us-central1/clusters/domino-gcp` (`1.35.8-gke.1796000`, UUID `00000000-0000-4000-8000-000000000000`) | `RUNNING` |
| **Node Pools** | `platform` (`n2-standard-8`, 4 nodes Ready), `compute` (`n2-highmem-8`, GCFS image streaming), `gpu` (`n1-highmem-8`, T4 autoscaling 0–2) | `RUNNING` |
| **Cloud Filestore (RWX)** | `projects/your-gcp-project-id/locations/us-central1-a/instances/domino-gcp` (`10.42.0.10:/share1`, 1 TB) | `READY` |
| **CMEK GCS Bucket** | `gs://dominodatalab-your-gcp-project-id-domino-gcp` | `READY` |
| **Artifact Registry** | `us-central1-docker.pkg.dev/your-gcp-project-id/domino-gcp-domino` (Immutable Tags) | `READY` |
| **Cloud KMS CryptoKey** | `projects/your-gcp-project-id/locations/us-central1/keyRings/domino-gcp/cryptoKeys/domino-gcp` (`86400s` rotation + GKE & GCS Service Agent IAM) | `ENABLED` |
| **Domino K8s Primitives** | `domino-platform`, `domino-compute`, `domino-system` namespaces, `dominodisk` default StorageClass, `my-cert` TLS Secret, `external-nginx` NetworkPolicy, Distributed Compute & Custom Certs ConfigMaps | `ACTIVE` |

---

## 6. Repository Structure

| Path | Purpose |
| :--- | :--- |
| [`terraform/`](terraform/) | Complete Terraform IaC module for Domino 6.3 on GKE (`apis.tf`, `kms.tf`, `network.tf`, `gke.tf`, `node_pools.tf`, `storage.tf`, `nfs-instance.tf`, `gcnv.tf`, `service-accounts.tf`, `gcr.tf`, `gcr-credential-refresher.tf`, `dns.tf`, `domino-config.tf`, `outputs.tf`) |
| [`terraform/examples/gke-main.tf`](terraform/examples/gke-main.tf) | Reconstructed standalone `gke-main.tf` root caller matching `ddlcloud_generator_gke/v1_0.py` |
| [`generated/domino.yml`](generated/domino.yml) | Auto-rendered Domino 6.3 installer configuration (`schema: '1.16'`) populated with live `your-gcp-project-id` Terraform outputs |
| [`generated/domino-nexus-dataplane.yml`](generated/domino-nexus-dataplane.yml) | Auto-rendered Domino Nexus Remote GKE Data Plane configuration (`--preset data-plane`) |
| [`k8s/`](k8s/) | Declarative Kubernetes manifests: Namespaces, `dominodisk` StorageClass, `external-nginx` `NetworkPolicy`, `domino-custom-certificates` `ConfigMap`, and Ray/Dask/MPI Workspace Tools |
| [`scripts/`](scripts/) | End-to-end automation scripts (`01_check_prerequisites.sh` through `04_upgrade_gke_cluster.sh` + `generate_architecture_diagrams.py`) |
| [`docs/DOMINO_GCP_DEPLOYMENT_PLAN.md`](docs/DOMINO_GCP_DEPLOYMENT_PLAN.md) | Comprehensive architectural & operational runbook synthesizing all Domino 6.3 GCP docs & sublinks |
| [`tests/validate_all.py`](tests/validate_all.py) | Automated verification suite testing Terraform state, outputs, `domino.yml` schema, K8s manifests, and SVG/PNG assets |
