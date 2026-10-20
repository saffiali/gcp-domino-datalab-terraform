locals {
  services_requiring_gcr = toset([
    "forge",
    "hephaestus",
  ])
}

resource "google_artifact_registry_repository" "domino" {
  count         = var.registry.create ? 1 : 0
  project       = var.project
  location      = local.region
  repository_id = "${var.deploy_id}-domino"
  description   = "Domino Data Lab 6.3 container image repository for environments and models"
  format        = "DOCKER"

  docker_config {
    immutable_tags = true
  }

  labels = var.tags

  depends_on = [google_project_service.required_apis]
}

resource "google_service_account" "gcr" {
  count        = var.registry.create ? 1 : 0
  project      = var.project
  account_id   = "${var.deploy_id}-gcr"
  display_name = "${var.deploy_id} Artifact Registry Builder Service Account"

  depends_on = [google_project_service.required_apis]
}

resource "google_project_iam_member" "gcr_storage" {
  count   = var.registry.create ? 1 : 0
  project = var.project
  role    = "roles/storage.admin"
  member  = "serviceAccount:${google_service_account.gcr[0].email}"
}

resource "google_artifact_registry_repository_iam_member" "domino" {
  count      = var.registry.create ? 1 : 0
  project    = google_artifact_registry_repository.domino[0].project
  location   = google_artifact_registry_repository.domino[0].location
  repository = google_artifact_registry_repository.domino[0].name
  role       = "roles/artifactregistry.repoAdmin"
  member     = "serviceAccount:${google_service_account.gcr[0].email}"
}

resource "google_service_account_iam_member" "gcr_wi" {
  for_each = var.registry.create ? local.services_requiring_gcr : toset([])

  service_account_id = google_service_account.gcr[0].name
  role               = "roles/iam.workloadIdentityUser"
  member             = "serviceAccount:${var.project}.svc.id.goog[${var.namespaces.compute}/${each.value}]"

  depends_on = [google_container_cluster.domino_cluster]
}
