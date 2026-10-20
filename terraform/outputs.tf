# ==============================================================================
# 1. Flat Outputs Matching Domino 6.3 Documentation & ddlcloud_generator_gke/v1_0.py
# ==============================================================================

output "google_filestore_ip_address" {
  description = "IPv4 address of the Cloud Filestore instance (or GCE NFS instance fallback) for storage_class.shared.nfs.server."
  value       = local.shared_nfs_server
}

output "google_filestore_file_share" {
  description = "NFS file share path (e.g., /share1 or /srv/domino) for storage_class.shared.nfs.mount_path."
  value       = local.shared_nfs_mount_path
}

output "google_external_dns" {
  description = "Cloud DNS managed zone details."
  value       = var.managed_dns.enabled ? var.managed_dns : null
}

output "google_bucket_name" {
  description = "Name of the CMEK-encrypted GCS bucket for blob_storage.backups.gcs.bucket_name."
  value       = google_storage_bucket.bucket.name
}

output "google_project" {
  description = "GCP Project ID for blob_storage.backups.gcs.project_name."
  value       = var.project
}

output "google_platform_service_account" {
  description = "Domino Platform GCP Service Account ID for blob_storage.backups.gcs.service_account_name."
  value       = google_service_account.platform_service_account.account_id
}

output "google_cluster_uuid" {
  description = "Unique identifier generated for the Domino GKE deployment."
  value       = random_uuid.cluster_uuid.result
}

output "google_gcr_service_account" {
  description = "Artifact Registry builder GCP Service Account email for image_building.cloud_registry_auth.gcp.service_account."
  value       = var.registry.create ? google_service_account.gcr[0].email : null
}

output "google_artifact_registry" {
  description = "Full Google Artifact Registry URL for external_docker_registry.url."
  value       = local.artifact_registry_url
}

output "nfs_instance_ip" {
  description = "Internal IPv4 address of the optional GCE NFS server VM."
  value       = var.storage.nfs_instance.enabled ? google_compute_instance.nfs[0].network_interface[0].network_ip : null
}

output "nfs_instance_path" {
  description = "Exported directory path on the optional GCE NFS server VM."
  value       = var.storage.nfs_instance.enabled ? local.nfs_dir : null
}

output "gcr_credential_refresher" {
  description = "GCR Credential Refresher service account email and Artifact Registry host."
  value = var.registry.create ? {
    service_account_email = google_service_account.gcr_credential_refresher[0].email
    registry_server       = "${google_artifact_registry_repository.domino[0].location}-docker.pkg.dev"
  } : null
}

output "gcnv_project_number" {
  description = "GCP Project Number for NetApp Volumes Trident configuration."
  value       = var.storage.gcnv.enabled ? data.google_project.domino.number : null
}

output "gcnv_location" {
  description = "Location of the NetApp Volumes storage pool."
  value       = var.storage.gcnv.enabled ? google_netapp_storage_pool.gcnv[0].location : null
}

output "gcnv_storage_pool_name" {
  description = "Name of the NetApp Volumes storage pool."
  value       = var.storage.gcnv.enabled ? google_netapp_storage_pool.gcnv[0].name : null
}

output "gcnv_service_account_email" {
  description = "Email of the Trident CSI Driver GCP service account."
  value       = var.storage.gcnv.enabled ? google_service_account.trident[0].email : null
}

output "gcnv_client_cidr" {
  description = "VPC subnet CIDR allowed to mount NetApp Volumes."
  value       = var.storage.gcnv.enabled ? google_compute_subnetwork.default.ip_cidr_range : null
}

output "gcnv_root_volume_name" {
  description = "Root volume name for NetApp Volumes."
  value       = var.storage.gcnv.enabled ? "${var.deploy_id}-root" : null
}

output "gcnv_export_policy_name" {
  description = "ONTAP export policy name for NetApp Volumes."
  value       = var.storage.gcnv.enabled ? "${var.deploy_id}-domino" : null
}

# ==============================================================================
# 2. Structured Outputs Matching dominodatalab/terraform-gcp-gke v3+
# ==============================================================================

output "bucket_name" {
  description = "Name of the GCS storage bucket."
  value       = google_storage_bucket.bucket.name
}

output "cluster" {
  description = "GKE cluster name, location, endpoint, and master version."
  value = {
    name           = google_container_cluster.domino_cluster.name
    location       = google_container_cluster.domino_cluster.location
    endpoint       = google_container_cluster.domino_cluster.endpoint
    master_version = google_container_cluster.domino_cluster.master_version
  }
}

output "dns" {
  description = "Cloud DNS managed zone configuration."
  value       = var.managed_dns.enabled ? var.managed_dns : null
}

output "domino_artifact_repository" {
  description = "Google Artifact Registry repository details."
  value = var.registry.create ? {
    location      = google_artifact_registry_repository.domino[0].location
    project       = google_artifact_registry_repository.domino[0].project
    repository_id = google_artifact_registry_repository.domino[0].repository_id
  } : null
}

output "google_filestore_instance" {
  description = "Cloud Filestore instance IP address and file share name."
  value = var.storage.filestore.enabled ? {
    ip_address = google_filestore_instance.nfs[0].networks[0].ip_addresses[0]
    file_share = google_filestore_instance.nfs[0].file_shares[0].name
  } : null
}

output "nfs_instance" {
  description = "GCE NFS VM IP address and NFS export path."
  value = var.storage.nfs_instance.enabled ? {
    ip_address = google_compute_instance.nfs[0].network_interface[0].network_ip
    nfs_path   = local.nfs_dir
  } : null
}

output "project" {
  description = "GCP Project ID."
  value       = var.project
}

output "service_accounts" {
  description = "Platform, Node Pool, and Artifact Registry GCP service accounts."
  value = {
    gke            = google_service_account.gke_node_pool
    platform       = google_service_account.platform_service_account
    gcr            = var.registry.create ? google_service_account.gcr[0] : null
    gcr_credential = var.registry.create ? google_service_account.gcr_credential_refresher[0] : null
  }
}

output "uuid" {
  description = "Cluster UUID."
  value       = random_uuid.cluster_uuid.result
}
