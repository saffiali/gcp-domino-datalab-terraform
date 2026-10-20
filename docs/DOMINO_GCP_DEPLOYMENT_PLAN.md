# Domino Data Lab 6.3 on Google Cloud Platform (GKE 1.35) — Complete Deployment Plan & Operational Runbook

![Domino Data Lab 6.3 on GCP Reference Architecture](../assets/01_domino_gcp_reference_architecture.svg)

---

## 1. Architecture & Sizing Reference (`gcp/architecture` + Sublinks)

### 1.1 Kubernetes Compatibility Matrix
Per [Kubernetes Infrastructure](https://docs.domino.ai/6.3/admin/architecture-and-deployment/kubernetes-infrastructure), **Domino 6.3.0** requires **Kubernetes `1.34` or `1.35`**. This Terraform suite pins `gke.k8s_version = "1.35."` on the `STABLE` release channel (`1.35.6-gke.1250001`).

### 1.2 Standard vs. Large Domino Platform Sizing
| Parameter | Standard Platform (`platform_sizing_tier = "standard"`) | Large Platform (`platform_sizing_tier = "large"`) |
| :--- | :--- | :--- |
| **Max Concurrent Executions** | Up to **300** concurrent executions | Up to **600** concurrent executions |
| **Platform Node Pool** | `4` nodes (`n2-highmem-8`: 8 vCPU, 64 GB RAM, 128 GB disk) | `5` nodes (`n2-highmem-16`: 16 vCPU, 64 GB RAM, 128 GB disk) |
| **Compute Node Pool** | `1–20` nodes (`n2-highmem-8`: 8 vCPU, 64 GB RAM, 400 GB disk) | `1–40` nodes (`n2-highmem-8` / `n2-highmem-16`, 400 GB disk) |
| **GPU Node Pool** | `0–4` nodes (`n1-highmem-8` + `nvidia-tesla-t4` / `p100` or `g2-standard-8` + `nvidia-l4`, 400 GB disk) | `0–10` nodes (`n1-highmem-8` / `g2-standard-8` / `a2-highgpu-1g`, 400 GB disk) |
| **Helm Release Overrides** | Default `fleetcommand-agent` resource requests/limits | Auto-injects `release_overrides` for `nucleus`, `elasticsearch`, `mongodb-replicaset`, `git`, `prometheus`, `cost-analyzer-prometheus`, `rabbitmq-ha`, and `data-plane` |

### 1.3 Storage Classes (`dominodisk` & `dominoshared`)
- **`dominodisk` (`ReadWriteOnce` Block Storage):** Backed by GCE Persistent Disk (`pd-balanced` / `pd-ssd`, `WaitForFirstConsumer`). Used by stateful Platform services (MongoDB, PostgreSQL, Git, Elasticsearch) and ephemeral user Workspace/Job execution volumes.
- **`dominoshared` (`ReadWriteMany` Shared Filesystem):** Used by Domino File System (DFS) Datasets and shared blobs across concurrent executions. Configured via one of three mutually exclusive backends in `terraform/variables.tf`:
  1. `storage.filestore.enabled = true`: Managed **Google Cloud Filestore** (`STANDARD` tier, `/share1`, `1024 GB` minimum, scalable to `10 TB+`).
  2. `storage.nfs_instance.enabled = true`: Self-managed **GCE NFS Server VM** (`n2-standard-2`, `/srv/domino`, `100 GB` `pd-standard`).
  3. `storage.gcnv.enabled = true`: Enterprise **Google Cloud NetApp Volumes** (`FLEX` `UNIFIED` ONTAP-mode storage pool with Trident CSI Workload Identity).

---

## 2. Prerequisites & Distributed Compute Clusters (`gcp/prerequisites` + Sublinks)

### 2.1 Release Artifacts & CLI Tooling
| Artifact | Domino 6.3.0 Pinned Version | Download URL / Source |
| :--- | :--- | :--- |
| **Domino Version** | `6.3.0` | [Domino 6.3 Releases](https://docs.domino.ai/6.3/admin/installation/releases) |
| **`ddlctl` CLI** | `0.6.4` | `https://mirrors.domino.tech/s3/domino-artifacts/ddlctl/0.6.4/ddlctl_0.6.4_linux_x86_64.tar.gz` |
| **Platform Operator Chart** | `0.6.4` | `https://mirrors.domino.tech/s3/domino-artifacts/platform-operator/platform-operator-0.6.4.tgz` |
| **`fleetcommand-agent` Tag** | `6.3.0.catalog-1df6e73` | `quay.io/domino/fleetcommand-agent:6.3.0.catalog-1df6e73` |

### 2.2 Distributed Compute Clusters (Ray, Dask, MPI)
Defined in [`k8s/04_distributed_clusters_workspace_tools.yaml`](../k8s/04_distributed_clusters_workspace_tools.yaml):
- **Ray (`2.55.1`):**
  - CPU Cluster Image: `quay.io/domino/ray-cluster-environment:ray2.55.1-py3.12-domino6.3`
  - GPU Cluster Image: `quay.io/domino/ray-cluster-gpu-environment:ray2.55.1-py3.12-domino6.3`
  - Workspace Image: `quay.io/domino/domino-ray-environment:ubuntu24-py3.12-r4.5-ray2.55.1-domino6.3`
  - Pluggable Workspace Tool: `ray-dashboard` (`httpProxy.port: 8265`)
- **Dask:**
  - Cluster Image: `quay.io/domino/dask-cluster-environment:ubuntu24-py3.12-domino6.3`
  - Pluggable Workspace Tool: `dask-webui` (`httpProxy.port: 8787`)
- **MPI (`4.1.4`):**
  - Central Configuration Record: `com.cerebro.domino.computegrid.kubernetes.mpi.ShortLived.MpiClustersEnabled = true`
  - Cluster Image: `quay.io/domino/mpi-cluster-environment:ubuntu24-py3.10-mpi-4.1.4-domino6.3` (Open MPI `4.1.2+`, Domino user UID `12574`).

---

## 3. Terraform Schema Mapping (`gcp/infrastructure` & `ddlcloud_generator_gke`)

![Domino 6.3 Network Perimeter and Workload Identity](../assets/02_domino_network_and_workload_identity_topology.svg)

### 3.1 Legacy v2 Documentation vs. `terraform-gcp-gke` v3+ Variable Mapping
| Legacy Domino 6.3 Doc Attribute (v2) | Current `terraform/` & `terraform-gcp-gke` (v3+) Attribute |
| :--- | :--- |
| `master_authorized_networks_config = [...]` | `gke.public_access = { enabled = true, cidrs = [...] }` |
| `node_pool_overrides = { ... }` | `node_pools = { platform = {...}, compute = {...}, gpu = {...} }` |
| `filestore_disabled = true` | `storage = { filestore = { enabled = false }, nfs_instance = { enabled = true } }` |
| `database_encryption_key_name` | `kms = { database_encryption_key_name = null }` |
| `kubeconfig_output_path` | `gke = { kubeconfig = { path = "kubeconfig" } }` |

### 3.2 Terraform Outputs to `domino.yml` Mapping
| Terraform Output (`outputs.tf`) | `generated/domino.yml` Target Field |
| :--- | :--- |
| `google_filestore_ip_address` | `storage_class.shared.nfs.server` |
| `google_filestore_file_share` | `storage_class.shared.nfs.mount_path` |
| `google_bucket_name` | `blob_storage.backups.gcs.bucket_name` & `internal_docker_registry.gcs_override.bucket` |
| `google_platform_service_account` | `blob_storage.backups.gcs.service_account_name` |
| `google_project` | `blob_storage.backups.gcs.project_name` |
| `google_gcr_service_account` | `image_building.cloud_registry_auth.gcp.service_account` |
| `google_artifact_registry` | `external_docker_registry.url` |

---

## 4. Platform Operator, Drift Detection, Keycloak & UAT (`gcp/deploy` + Sublinks)

![Domino 6.3 Deployment Pipeline and Day-2 Lifecycle](../assets/03_domino_deployment_and_nexus_lifecycle.svg)

### 4.1 Platform Operator & `HelmRelease` Drift Reconciliation
```bash
# Inspect Domino Custom Resource state
ddlctl get domino

# List all HelmReleases and check for 5-minute drift detection status
ddlctl get helmrelease --all
ddlctl get helmrelease -A --status stalled=true

# View live manifest diff and force reconciliation of a drifted release
ddlctl diff helmrelease <release-name>
ddlctl reconcile helmrelease <release-name> --reset --force
```

### 4.2 Keycloak (`DominoRealm`) Initial Onboarding
1. Retrieve the initial Keycloak administrator password:
   ```bash
   kubectl get secret -n domino-platform keycloak-http -o jsonpath='{.data.password}' | base64 -d
   ```
2. Navigate to `https://<DOMINO_HOSTNAME>/auth/`, click **Administration Console**, and sign in as `keycloak`.
3. Select the **`DominoRealm`** realm in the top-left dropdown:
   - **Self-Registration Method:** Under **Realm Settings > Login**, toggle **User Registration** to **ON**, click **Save**, sign up at `https://<DOMINO_HOSTNAME>`, and toggle **User Registration** back to **OFF**.
   - **Admin-Provisioned Method:** Under **Manage > Users > Add user**, set Username/Email (`Email Verified = ON`), set password under **Credentials**, and under **Role Mappings > Client Roles > `domino-play`**, assign the **`User`** role.
4. Promote the first user to Domino Admin via `https://<DOMINO_HOSTNAME>/admin` (**Admin > Advanced > Users**).

### 4.3 User Acceptance Testing (UAT) Verification Matrix
| UAT Category | Validation Check |
| :--- | :--- |
| **Admin & Infrastructure** | Verify active `platform` and `compute` nodes in **Admin > Infrastructure**, check **Control Center**, and set `customer_name` / `deployment_name` in Central Config |
| **Compute Environments** | Create a custom environment, add a `pip` package and pre/post-run scripts, build via Hephaestus, and confirm image push to Google Artifact Registry (`domino-gcp-domino`) |
| **Interactive Workspaces** | Launch **JupyterLab**, **Jupyter**, **RStudio**, and **VS Code** sessions; execute Python/R code; verify file sync to Domino File System (DFS) and Git |
| **Datasets & EDVs** | Create a shared Dataset and snapshot on `dominoshared` (`ReadWriteMany` Cloud Filestore `/share1`); mount/unmount an External Data Volume (EDV) |
| **Apps, Endpoints & Clusters** | Publish a Flask / R Shiny App, deploy a real-time Model Endpoint and send test prediction requests, and attach on-demand Ray / Dask / Spark clusters |
