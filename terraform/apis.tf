locals {
  location_parts = split("-", var.location)
  region         = "${local.location_parts[0]}-${local.location_parts[1]}"
  is_regional    = length(local.location_parts) == 2
  zone           = local.is_regional ? data.google_compute_zones.zones.names[0] : var.location

  required_apis = toset([
    "artifactregistry.googleapis.com",
    "cloudkms.googleapis.com",
    "compute.googleapis.com",
    "container.googleapis.com",
    "containerfilesystem.googleapis.com",
    "dns.googleapis.com",
    "file.googleapis.com",
    "iam.googleapis.com",
    "iamcredentials.googleapis.com",
    "logging.googleapis.com",
    "monitoring.googleapis.com",
    "servicenetworking.googleapis.com",
    "storage.googleapis.com",
  ])
}

data "google_project" "domino" {
  project_id = var.project
}

data "google_compute_zones" "zones" {
  project    = var.project
  region     = local.region
  depends_on = [google_project_service.required_apis]
}

resource "google_project_service" "required_apis" {
  for_each = local.required_apis

  project            = var.project
  service            = each.value
  disable_on_destroy = false
}

# Ensure the GKE Service Agent exists before binding Cloud KMS permissions
resource "google_project_service_identity" "gke_sa" {
  provider = google-beta
  project  = var.project
  service  = "container.googleapis.com"

  depends_on = [google_project_service.required_apis]
}

resource "random_uuid" "cluster_uuid" {
}
