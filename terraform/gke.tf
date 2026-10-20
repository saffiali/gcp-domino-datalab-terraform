data "google_container_engine_versions" "k8s_version" {
  location       = var.location
  project        = var.project
  version_prefix = var.gke.k8s_version

  depends_on = [google_project_service.required_apis]
}

resource "google_container_cluster" "domino_cluster" {
  provider = google-beta

  name                     = var.deploy_id
  project                  = var.project
  location                 = var.location
  node_locations           = local.is_regional && length(var.default_node_locations) > 0 ? var.default_node_locations : null
  remove_default_node_pool = true
  initial_node_count       = 1
  deletion_protection      = false

  network    = google_compute_network.vpc_network.id
  subnetwork = google_compute_subnetwork.default.id

  resource_labels = merge({
    "deploy_id" = var.deploy_id
  }, var.tags)

  ip_allocation_policy {
    cluster_ipv4_cidr_block  = ""
    services_ipv4_cidr_block = ""
  }

  private_cluster_config {
    enable_private_nodes    = true
    enable_private_endpoint = !var.gke.public_access.enabled
    master_ipv4_cidr_block  = var.master_ipv4_cidr_block
    master_global_access_config {
      enabled = true
    }
  }

  dynamic "master_authorized_networks_config" {
    for_each = var.gke.public_access.enabled ? [1] : []
    content {
      dynamic "cidr_blocks" {
        for_each = toset(var.gke.public_access.cidrs)
        content {
          cidr_block = cidr_blocks.value
        }
      }
    }
  }

  release_channel {
    channel = var.gke.release_channel
  }

  min_master_version = data.google_container_engine_versions.k8s_version.latest_master_version

  database_encryption {
    state    = "ENCRYPTED"
    key_name = var.kms.database_encryption_key_name == null ? google_kms_crypto_key.crypto_key[0].id : var.kms.database_encryption_key_name
  }

  workload_identity_config {
    workload_pool = "${var.project}.svc.id.goog"
  }

  network_policy {
    enabled  = var.gke.advanced_datapath ? false : var.gke.network_policies
    provider = var.gke.advanced_datapath ? "PROVIDER_UNSPECIFIED" : (var.gke.network_policies ? "CALICO" : "PROVIDER_UNSPECIFIED")
  }

  datapath_provider = var.gke.advanced_datapath ? "ADVANCED_DATAPATH" : "LEGACY_DATAPATH"

  vertical_pod_autoscaling {
    enabled = var.gke.vertical_pod_autoscaling
  }

  depends_on = [
    google_project_service.required_apis,
    google_project_service_identity.gke_sa,
    google_kms_crypto_key_iam_binding.binding,
  ]

  lifecycle {
    ignore_changes = [
      initial_node_count,
      node_config,
    ]
  }
}

resource "google_compute_firewall" "master_webhooks" {
  project     = var.project
  name        = "${var.deploy_id}-gke-master-webhooks"
  network     = google_compute_network.vpc_network.name
  description = "Allow GKE master control plane access to Domino admission webhooks and Kubelet API."

  allow {
    protocol = "tcp"
    ports    = var.gke.control_plane_ports
  }

  source_ranges = [google_container_cluster.domino_cluster.private_cluster_config[0].master_ipv4_cidr_block]
  target_tags   = [var.deploy_id]
}
