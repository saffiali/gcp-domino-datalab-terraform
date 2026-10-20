locals {
  nfs_dir  = "/srv/domino"
  nfs_disk = "${var.deploy_id}-nfs"
}

resource "google_compute_instance" "nfs" {
  count        = var.storage.nfs_instance.enabled ? 1 : 0
  project      = var.project
  name         = "${var.deploy_id}-nfs"
  machine_type = var.storage.nfs_instance.instance_type
  zone         = local.zone

  tags   = [var.deploy_id, "${var.deploy_id}-node-pool"]
  labels = var.tags

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-12"
    }
  }

  attached_disk {
    source      = google_compute_disk.nfs[0].self_link
    device_name = local.nfs_disk
  }

  network_interface {
    subnetwork = google_compute_subnetwork.default.self_link
  }

  metadata_startup_script = templatefile("${path.module}/templates/nfs-install.sh", {
    disk_name = local.nfs_disk
    nfs_dir   = local.nfs_dir
    cidr      = google_compute_subnetwork.default.ip_cidr_range
  })

  service_account {
    email  = google_service_account.gke_node_pool.email
    scopes = ["cloud-platform"]
  }

  allow_stopping_for_update = true

  lifecycle {
    ignore_changes = [attached_disk]
  }
}

resource "google_compute_disk" "nfs" {
  count   = var.storage.nfs_instance.enabled ? 1 : 0
  project = var.project
  name    = "${var.deploy_id}-nfs"
  type    = var.storage.nfs_instance.disk_type
  zone    = local.zone
  size    = var.storage.nfs_instance.capacity
  labels  = var.tags
}

resource "google_compute_firewall" "nfs" {
  count   = var.storage.nfs_instance.enabled ? 1 : 0
  project = var.project
  name    = "${var.deploy_id}-nfs"
  network = google_compute_network.vpc_network.name

  allow {
    protocol = "tcp"
    ports    = ["111", "2049"]
  }

  allow {
    protocol = "udp"
    ports    = ["111", "2049"]
  }

  source_tags = [var.deploy_id]
  target_tags = [var.deploy_id]
}
