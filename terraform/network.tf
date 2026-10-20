resource "google_compute_network" "vpc_network" {
  project                 = var.project
  name                    = var.deploy_id
  auto_create_subnetworks = false

  depends_on = [google_project_service.required_apis]
}

resource "google_compute_subnetwork" "default" {
  project                  = var.project
  name                     = var.deploy_id
  ip_cidr_range            = var.network_cidr
  region                   = local.region
  network                  = google_compute_network.vpc_network.id
  private_ip_google_access = true
}

resource "google_compute_router" "router" {
  project = var.project
  name    = var.deploy_id
  region  = google_compute_subnetwork.default.region
  network = google_compute_network.vpc_network.id
}

resource "google_compute_router_nat" "nat" {
  project                            = var.project
  name                               = var.deploy_id
  router                             = google_compute_router.router.name
  region                             = google_compute_router.router.region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"

  log_config {
    enable = true
    filter = "ERRORS_ONLY"
  }
}

resource "google_compute_global_address" "gcnv" {
  count         = var.storage.gcnv.enabled ? 1 : 0
  project       = var.project
  name          = "${var.deploy_id}-gcnv-peering"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 24
  network       = google_compute_network.vpc_network.id
}

resource "google_service_networking_connection" "gcnv" {
  count                   = var.storage.gcnv.enabled ? 1 : 0
  network                 = google_compute_network.vpc_network.id
  service                 = "netapp.servicenetworking.goog"
  reserved_peering_ranges = [google_compute_global_address.gcnv[0].name]

  deletion_policy = "ABANDON"
}
