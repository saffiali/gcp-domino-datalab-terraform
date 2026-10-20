locals {
  shared_nfs_server = var.storage.filestore.enabled ? google_filestore_instance.nfs[0].networks[0].ip_addresses[0] : (
    var.storage.nfs_instance.enabled ? google_compute_instance.nfs[0].network_interface[0].network_ip : ""
  )

  shared_nfs_mount_path = var.storage.filestore.enabled ? "/${google_filestore_instance.nfs[0].file_shares[0].name}" : (
    var.storage.nfs_instance.enabled ? local.nfs_dir : "/share1"
  )

  artifact_registry_url = var.registry.create ? "${google_artifact_registry_repository.domino[0].location}-docker.pkg.dev/${google_artifact_registry_repository.domino[0].project}/${google_artifact_registry_repository.domino[0].repository_id}" : ""
}

resource "local_file" "domino_yml" {
  filename = "${path.module}/../generated/domino.yml"
  content = templatefile("${path.module}/templates/domino.yml.tftpl", {
    deploy_id                     = var.deploy_id
    domino_hostname               = var.domino_hostname
    domino_version                = var.domino_version
    fleetcommand_agent_tag        = var.fleetcommand_agent_tag
    platform_sizing_tier          = var.platform_sizing_tier
    namespace_platform            = var.namespaces.platform
    namespace_compute             = var.namespaces.compute
    namespace_system              = var.namespaces.system
    shared_nfs_server             = local.shared_nfs_server
    shared_nfs_mount_path         = local.shared_nfs_mount_path
    google_bucket_name            = google_storage_bucket.bucket.name
    google_platform_sa_account_id = google_service_account.platform_service_account.account_id
    google_platform_sa_email      = google_service_account.platform_service_account.email
    google_project                = var.project
    google_gcr_service_account    = var.registry.create ? google_service_account.gcr[0].email : ""
    google_gcr_cred_refresher_sa  = var.registry.create ? google_service_account.gcr_credential_refresher[0].email : ""
    google_artifact_registry      = local.artifact_registry_url
    gpu_enabled                   = var.node_pools.gpu.max_count > 0
  })
}

resource "local_file" "domino_nexus_dataplane_yml" {
  filename = "${path.module}/../generated/domino-nexus-dataplane.yml"
  content = templatefile("${path.module}/templates/domino-nexus-dataplane.yml.tftpl", {
    deploy_id             = var.deploy_id
    domino_hostname       = var.domino_hostname
    namespace_compute     = var.namespaces.compute
    shared_nfs_server     = local.shared_nfs_server
    shared_nfs_mount_path = local.shared_nfs_mount_path
    gpu_enabled           = var.node_pools.gpu.max_count > 0
  })
}
