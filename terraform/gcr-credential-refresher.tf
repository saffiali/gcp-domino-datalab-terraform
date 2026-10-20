resource "google_service_account" "gcr_credential_refresher" {
  count        = var.registry.create ? 1 : 0
  project      = var.project
  account_id   = "${var.deploy_id}-gcr-cred"
  display_name = "${var.deploy_id} GCR Credential Refresher Service Account"

  depends_on = [google_project_service.required_apis]
}

resource "google_artifact_registry_repository_iam_member" "gcr_credential_refresher" {
  count      = var.registry.create ? 1 : 0
  project    = google_artifact_registry_repository.domino[0].project
  location   = google_artifact_registry_repository.domino[0].location
  repository = google_artifact_registry_repository.domino[0].name
  role       = "roles/artifactregistry.reader"
  member     = "serviceAccount:${google_service_account.gcr_credential_refresher[0].email}"
}

resource "google_service_account_iam_member" "gcr_credential_refresher_wi" {
  count              = var.registry.create ? 1 : 0
  service_account_id = google_service_account.gcr_credential_refresher[0].name
  role               = "roles/iam.workloadIdentityUser"
  member             = "serviceAccount:${var.project}.svc.id.goog[${var.namespaces.platform}/nucleus-gcr-credential-refresher]"

  depends_on = [google_container_cluster.domino_cluster]
}

resource "google_service_account_iam_member" "gcr_credential_refresher_token_creator" {
  count              = var.registry.create ? 1 : 0
  service_account_id = google_service_account.gcr_credential_refresher[0].name
  role               = "roles/iam.serviceAccountTokenCreator"
  member             = "serviceAccount:${google_service_account.gcr_credential_refresher[0].email}"
}
