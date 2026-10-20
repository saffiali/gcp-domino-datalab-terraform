variable "project" {
  description = "GCP Project ID where Domino Data Lab 6.3 infrastructure will be provisioned."
  type        = string
  default     = "your-gcp-project-id"
}

variable "deploy_id" {
  description = "Domino Deployment ID (3-20 lowercase alphanumeric or hyphen characters, used as resource prefix)."
  type        = string
  default     = "domino-gcp"

  validation {
    condition     = can(regex("^([a-z0-9-]){3,20}$", var.deploy_id))
    error_message = "Variable deploy_id must be 3-20 characters long and contain only lowercase letters, numbers, and hyphens."
  }

  validation {
    condition     = can(regex("^[a-z]", var.deploy_id))
    error_message = "Variable deploy_id must start with a lowercase letter."
  }

  validation {
    condition     = can(regex("[a-z0-9]$", var.deploy_id))
    error_message = "Variable deploy_id must end with a lowercase letter or number."
  }
}

variable "location" {
  description = "GCP Region (e.g., 'us-central1' for Regional HA GKE control plane) or Zone (e.g., 'us-central1-a')."
  type        = string
  default     = "us-central1"
}

variable "default_node_locations" {
  description = "Default Compute Engine zones within the region for GKE worker node pools when node_locations is not explicitly set on a pool (avoids us-central1-c N2 stockouts)."
  type        = list(string)
  default     = ["us-central1-a", "us-central1-b"]
}

variable "domino_hostname" {
  description = "Fully qualified domain name (FQDN) for the Domino Data Lab deployment (must not be a subdomain of another Domino deployment)."
  type        = string
  default     = "domino.gke-demos.example.com"
}

variable "domino_version" {
  description = "Domino Data Lab release version."
  type        = string
  default     = "6.3.0"
}

variable "fleetcommand_agent_tag" {
  description = "Domino 6.3.0 fleetcommand-agent container tag from https://docs.domino.ai/6.3/admin/installation/releases."
  type        = string
  default     = "6.3.0.catalog-1df6e73"
}

variable "ddlctl_version" {
  description = "Domino Platform Operator CLI (ddlctl) version for Domino 6.3.0."
  type        = string
  default     = "0.6.4"
}

variable "platform_sizing_tier" {
  description = "Domino Platform sizing profile: 'standard' (up to 300 concurrent executions) or 'large' (up to 600 concurrent executions with release_overrides)."
  type        = string
  default     = "standard"

  validation {
    condition     = contains(["standard", "large"], var.platform_sizing_tier)
    error_message = "platform_sizing_tier must be either 'standard' or 'large'."
  }
}

variable "namespaces" {
  description = "Kubernetes namespaces used by Domino Platform, Compute, and System tiers."
  type = object({
    platform = optional(string, "domino-platform")
    compute  = optional(string, "domino-compute")
    system   = optional(string, "domino-system")
  })
  default = {}
}

variable "network_cidr" {
  description = "Primary IPv4 CIDR range for the Domino VPC subnetwork."
  type        = string
  default     = "10.138.0.0/20"
}

variable "master_ipv4_cidr_block" {
  description = "Private /28 IPv4 CIDR block for the GKE master control plane VPC peering."
  type        = string
  default     = "172.16.1.0/28"
}

variable "allowed_ssh_ranges" {
  description = "Additional IPv4 CIDR blocks permitted to SSH (TCP/22) into GKE nodes alongside Google IAP (35.235.240.0/20)."
  type        = list(string)
  default     = []
}

variable "migration_permissions" {
  description = "Grant broad temporary IAM permissions to the platform service account during migration."
  type        = bool
  default     = false
}

variable "tags" {
  description = "GCP resource labels applied across all Domino infrastructure resources."
  type        = map(string)
  default = {
    managed-by  = "terraform"
    application = "domino-datalab"
    version     = "6-3-0"
  }
}

variable "storage" {
  description = "Domino shared filesystem (dominoshared ReadWriteMany) and object storage (GCS) configuration. Exactly one shared store (filestore, nfs_instance, or gcnv) may be enabled."
  type = object({
    filestore = optional(object({
      enabled  = optional(bool, true)
      capacity = optional(number, 1024)
      tier     = optional(string, "STANDARD")
    }), {})
    nfs_instance = optional(object({
      enabled       = optional(bool, false)
      capacity      = optional(number, 100)
      instance_type = optional(string, "n2-standard-2")
      disk_type     = optional(string, "pd-standard")
    }), {})
    gcs = optional(object({
      bucket_name_override      = optional(string, null)
      force_destroy_on_deletion = optional(bool, true)
    }), {})
    gcnv = optional(object({
      enabled           = optional(bool, false)
      pool_capacity_gib = optional(number, 1024)
      trident_namespace = optional(string, "trident")
      regional          = optional(bool, false)
      primary_zone      = optional(string, null)
      replica_zone      = optional(string, null)
    }), {})
  })
  default = {}

  validation {
    condition = length([
      for store_enabled in [
        var.storage.filestore.enabled,
        var.storage.nfs_instance.enabled,
        var.storage.gcnv.enabled,
      ] : store_enabled if store_enabled
    ]) <= 1
    error_message = "At most one shared storage backend (storage.filestore, storage.nfs_instance, or storage.gcnv) can be enabled at a time."
  }
}

variable "registry" {
  description = "Google Artifact Registry configuration for Domino environment and model images."
  type = object({
    create = optional(bool, true)
  })
  default = {}
}

variable "managed_dns" {
  description = "Optional Cloud DNS managed zone, static IPv4 reservation, external-dns, and cert-manager Workload Identity configuration."
  type = object({
    enabled                  = optional(bool, false)
    name                     = optional(string)
    dns_name                 = optional(string)
    service_prefixes         = optional(list(string), [])
    SetupExternalDNS         = optional(bool, false)
    ExternalDNSNamespace     = optional(string, "default")
    SetupCertManager         = optional(bool, false)
    CertManagerNamespace     = optional(string, "default")
    CertManagerResourcesName = optional(string, "cert-manager")
  })
  default = {}
}

variable "kms" {
  description = "Cloud KMS configuration for GKE Application-Layer Secrets Encryption (database_encryption) and GCS CMEK."
  type = object({
    database_encryption_key_name = optional(string, null)
  })
  default = {}
}

variable "gke" {
  description = "GKE cluster configuration aligned with Domino 6.3 Kubernetes compatibility (1.34 or 1.35)."
  type = object({
    k8s_version     = optional(string, "1.35.")
    release_channel = optional(string, "STABLE")
    public_access = optional(object({
      enabled = optional(bool, true)
      cidrs   = optional(list(string), ["0.0.0.0/0"])
    }), {})
    control_plane_ports = optional(list(string), [
      "6443",  # Kubernetes API / webhooks
      "8080",  # HTTP webhook services
      "8443",  # NGINX Ingress validating admission webhook
      "9443",  # Cert-manager / operator admission webhooks
      "10250", # Kubelet API (exec/logs)
      "15017", # Istio / service mesh webhook
    ])
    advanced_datapath        = optional(bool, true)
    network_policies         = optional(bool, false)
    vertical_pod_autoscaling = optional(bool, true)
    kubeconfig = optional(object({
      path = optional(string, null)
    }), {})
  })
  default = {}
}

variable "node_pools" {
  description = "GKE node pools for Domino Platform, Compute, and GPU workloads."
  type = object({
    compute = optional(object({
      min_count       = optional(number, 0)
      max_count       = optional(number, 10)
      initial_count   = optional(number, 1)
      max_pods        = optional(number, 30)
      preemptible     = optional(bool, false)
      disk_size_gb    = optional(number, 400)
      image_type      = optional(string, "COS_CONTAINERD")
      instance_type   = optional(string, "n2-highmem-8")
      gpu_accelerator = optional(string, null)
      labels = optional(map(string), {
        "dominodatalab.com/node-pool"  = "default"
        "domino/build-node"            = "true"
        "dominodatalab.com/build-node" = "true"
      })
      taints         = optional(list(string), [])
      node_locations = optional(list(string), null)
    }), {})

    platform = optional(object({
      min_count       = optional(number, 1)
      max_count       = optional(number, 5)
      initial_count   = optional(number, 2)
      max_pods        = optional(number, 60)
      preemptible     = optional(bool, false)
      disk_size_gb    = optional(number, 128)
      image_type      = optional(string, "COS_CONTAINERD")
      instance_type   = optional(string, "n2-highmem-8")
      gpu_accelerator = optional(string, null)
      labels = optional(map(string), {
        "dominodatalab.com/node-pool" = "platform"
      })
      taints         = optional(list(string), [])
      node_locations = optional(list(string), null)
    }), {})

    gpu = optional(object({
      min_count       = optional(number, 0)
      max_count       = optional(number, 2)
      initial_count   = optional(number, 0)
      max_pods        = optional(number, 30)
      preemptible     = optional(bool, false)
      disk_size_gb    = optional(number, 400)
      image_type      = optional(string, "COS_CONTAINERD")
      instance_type   = optional(string, "n1-highmem-8")
      gpu_accelerator = optional(string, "nvidia-tesla-t4")
      labels = optional(map(string), {
        "dominodatalab.com/node-pool" = "default-gpu"
        "nvidia.com/gpu"              = "true"
      })
      taints         = optional(list(string), ["nvidia.com/gpu=true:NoExecute"])
      node_locations = optional(list(string), null)
    }), {})
  })
  default = {}
}

variable "additional_node_pools" {
  description = "Map of additional custom GKE node pools (e.g., high-memory or A100/L4 GPU pools) to provision."
  type = map(object({
    min_count       = optional(number, 0)
    max_count       = optional(number, 10)
    initial_count   = optional(number, 0)
    max_pods        = optional(number, 30)
    preemptible     = optional(bool, false)
    disk_size_gb    = optional(number, 400)
    image_type      = optional(string, "COS_CONTAINERD")
    instance_type   = optional(string, "n2-highmem-16")
    gpu_accelerator = optional(string, null)
    labels = optional(map(string), {
      "dominodatalab.com/node-pool" = "custom"
    })
    taints         = optional(list(string), [])
    node_locations = optional(list(string), null)
  }))
  default = {}
}
