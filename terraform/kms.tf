data "google_storage_project_service_account" "gcs_account" {
  project    = var.project
  depends_on = [google_project_service.required_apis]
}

resource "google_kms_key_ring" "key_ring" {
  count    = var.kms.database_encryption_key_name == null ? 1 : 0
  project  = var.project
  name     = var.deploy_id
  location = local.region

  depends_on = [google_project_service.required_apis]

  lifecycle {
    prevent_destroy = false
  }
}

resource "google_kms_crypto_key" "crypto_key" {
  count           = var.kms.database_encryption_key_name == null ? 1 : 0
  name            = var.deploy_id
  key_ring        = google_kms_key_ring.key_ring[0].id
  purpose         = "ENCRYPT_DECRYPT"
  rotation_period = "86400s"

  labels = var.tags

  lifecycle {
    prevent_destroy = false
  }
}

# Automatically grant Cloud KMS Encrypter/Decrypter to BOTH:
# 1. Google Cloud Storage Service Agent (for GCS CMEK encryption)
# 2. Google Kubernetes Engine Service Agent (for GKE etcd Application-Layer Secrets Encryption)
resource "google_kms_crypto_key_iam_binding" "binding" {
  count         = var.kms.database_encryption_key_name == null ? 1 : 0
  crypto_key_id = google_kms_crypto_key.crypto_key[0].id
  role          = "roles/cloudkms.cryptoKeyEncrypterDecrypter"

  members = [
    "serviceAccount:${data.google_storage_project_service_account.gcs_account.email_address}",
    "serviceAccount:service-${data.google_project.domino.number}@container-engine-robot.iam.gserviceaccount.com",
  ]

  depends_on = [
    google_project_service.required_apis,
    google_project_service_identity.gke_sa,
  ]
}
