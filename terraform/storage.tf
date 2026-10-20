locals {
  bucket_name = var.storage.gcs.bucket_name_override != null ? var.storage.gcs.bucket_name_override : "dominodatalab-${var.project}-${var.deploy_id}"
}

resource "google_storage_bucket" "bucket" {
  project       = var.project
  name          = local.bucket_name
  location      = local.region
  force_destroy = var.storage.gcs.force_destroy_on_deletion

  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"

  versioning {
    enabled = true
  }

  encryption {
    default_kms_key_name = var.kms.database_encryption_key_name == null ? google_kms_crypto_key.crypto_key[0].id : var.kms.database_encryption_key_name
  }

  labels = var.tags

  depends_on = [
    google_project_service.required_apis,
    google_kms_crypto_key_iam_binding.binding,
  ]
}

resource "google_filestore_instance" "nfs" {
  count    = var.storage.filestore.enabled ? 1 : 0
  project  = var.project
  name     = var.deploy_id
  location = local.zone
  tier     = var.storage.filestore.tier

  file_shares {
    capacity_gb = var.storage.filestore.capacity
    name        = "share1"
  }

  networks {
    network = google_compute_network.vpc_network.name
    modes   = ["MODE_IPV4"]
  }

  labels = var.tags

  depends_on = [google_project_service.required_apis]
}
