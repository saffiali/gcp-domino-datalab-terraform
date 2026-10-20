locals {
  node_pools = merge(var.node_pools, var.additional_node_pools)
}

resource "google_service_account" "gke_node_pool" {
  project      = var.project
  account_id   = "${var.deploy_id}-gke"
  display_name = "${var.deploy_id} GKE Node Service Account"

  depends_on = [google_project_service.required_apis]
}

resource "google_project_iam_member" "gke_node_pool" {
  for_each = toset([
    "roles/logging.logWriter",
    "roles/monitoring.metricWriter",
    "roles/monitoring.viewer",
    "roles/stackdriver.resourceMetadata.writer",
    "roles/storage.objectViewer",
    "roles/artifactregistry.reader",
  ])

  project = var.project
  role    = each.value
  member  = "serviceAccount:${google_service_account.gke_node_pool.email}"
}

resource "google_container_node_pool" "node_pools" {
  provider = google-beta
  for_each = local.node_pools

  project  = var.project
  name     = each.key
  location = google_container_cluster.domino_cluster.location
  cluster  = google_container_cluster.domino_cluster.name

  node_locations = each.value.node_locations != null ? each.value.node_locations : (
    local.is_regional && length(var.default_node_locations) > 0 ? var.default_node_locations : null
  )

  initial_node_count = each.value.initial_count
  max_pods_per_node  = each.value.max_pods

  version = data.google_container_engine_versions.k8s_version.latest_node_version

  autoscaling {
    min_node_count = each.value.min_count
    max_node_count = each.value.max_count
  }

  management {
    auto_repair  = true
    auto_upgrade = true
  }

  node_config {
    preemptible  = each.value.preemptible
    disk_size_gb = each.value.disk_size_gb
    disk_type    = "pd-balanced"
    image_type   = each.value.image_type
    machine_type = each.value.instance_type
    tags         = [var.deploy_id, "${var.deploy_id}-node-pool"]

    gcfs_config {
      enabled = each.value.image_type == "COS_CONTAINERD"
    }

    metadata = {
      disable-legacy-endpoints = "true"
    }

    dynamic "guest_accelerator" {
      for_each = each.value.gpu_accelerator == null ? [] : [1]
      content {
        type  = each.value.gpu_accelerator
        count = 1
      }
    }

    service_account = google_service_account.gke_node_pool.email
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]

    labels = merge(each.value.labels, var.tags)

    dynamic "taint" {
      for_each = toset(each.value.taints)

      content {
        key   = split("=", taint.value)[0]
        value = split(":", split("=", taint.value)[1])[0]
        effect = lookup({
          "NoSchedule"       = "NO_SCHEDULE"
          "PreferNoSchedule" = "PREFER_NO_SCHEDULE"
          "NoExecute"        = "NO_EXECUTE"
          "NO_SCHEDULE"      = "NO_SCHEDULE"
          "NO_EXECUTE"       = "NO_EXECUTE"
        }, split(":", taint.value)[1], "NO_EXECUTE")
      }
    }

    workload_metadata_config {
      mode = "GKE_METADATA"
    }
  }

  lifecycle {
    ignore_changes = [
      initial_node_count,
    ]
  }
}

resource "google_compute_firewall" "iap_tcp_forwarding" {
  project = var.project
  name    = "${var.deploy_id}-allow-ssh-from-iap"
  network = google_compute_network.vpc_network.name

  direction = "INGRESS"

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  # https://cloud.google.com/iap/docs/using-tcp-forwarding
  source_ranges = distinct(concat(var.allowed_ssh_ranges, ["35.235.240.0/20"]))
  target_tags   = ["${var.deploy_id}-node-pool"]
}
