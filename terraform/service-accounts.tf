locals {
  services_requiring_workload_identity = toset([
    "docker-registry",
    "domino-data-importer",
    "git",
    "nucleus",
  ])
}

resource "google_service_account" "platform_service_account" {
  project      = var.project
  account_id   = "${var.deploy_id}-platform"
  display_name = "${var.deploy_id} Domino Platform Service Account"

  depends_on = [google_project_service.required_apis]
}

resource "google_project_iam_member" "platform_service_account" {
  for_each = toset(var.migration_permissions ? [
    "roles/logging.logWriter",
    "roles/monitoring.metricWriter",
    "roles/monitoring.viewer",
    "roles/stackdriver.resourceMetadata.writer",
    "roles/storage.admin",
    ] : [
    "roles/logging.logWriter",
    "roles/monitoring.metricWriter",
    "roles/monitoring.viewer",
    "roles/stackdriver.resourceMetadata.writer",
  ])

  project = var.project
  role    = each.value
  member  = "serviceAccount:${google_service_account.platform_service_account.email}"
}

resource "google_storage_bucket_iam_member" "bucket_member" {
  bucket = google_storage_bucket.bucket.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.platform_service_account.email}"
}

resource "google_service_account_iam_member" "workload_identity" {
  for_each = local.services_requiring_workload_identity

  service_account_id = google_service_account.platform_service_account.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "serviceAccount:${var.project}.svc.id.goog[${var.namespaces.platform}/${each.value}]"

  depends_on = [google_container_cluster.domino_cluster]
}
