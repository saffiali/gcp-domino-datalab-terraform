locals {
  gcnv_primary_zone = coalesce(
    var.storage.gcnv.primary_zone,
    local.zone,
  )

  gcnv_available_replica_zones = [
    for z in data.google_compute_zones.zones.names : z
    if z != local.gcnv_primary_zone
  ]

  gcnv_replica_zone = var.storage.gcnv.regional ? coalesce(
    var.storage.gcnv.replica_zone,
    local.gcnv_available_replica_zones[0],
  ) : null

  gcnv_location = var.storage.gcnv.regional ? local.region : local.gcnv_primary_zone
}

resource "google_netapp_storage_pool" "gcnv" {
  count    = var.storage.gcnv.enabled ? 1 : 0
  project  = var.project
  name     = "${var.deploy_id}-gcnv"
  location = local.gcnv_location

  service_level = "FLEX"
  type          = "UNIFIED"
  mode          = "ONTAP"
  capacity_gib  = var.storage.gcnv.pool_capacity_gib
  network       = google_compute_network.vpc_network.id

  zone         = var.storage.gcnv.regional ? local.gcnv_primary_zone : null
  replica_zone = local.gcnv_replica_zone

  labels = var.tags

  depends_on = [google_service_networking_connection.gcnv]
}

resource "google_service_account" "trident" {
  count        = var.storage.gcnv.enabled ? 1 : 0
  project      = var.project
  account_id   = "${var.deploy_id}-trident"
  display_name = "${var.deploy_id} Trident CSI Driver Service Account"
}

resource "google_project_iam_member" "trident_gcnv_admin" {
  count   = var.storage.gcnv.enabled ? 1 : 0
  project = var.project
  role    = "roles/netapp.admin"
  member  = "serviceAccount:${google_service_account.trident[0].email}"
}

resource "google_service_account_iam_member" "trident_wi" {
  count              = var.storage.gcnv.enabled ? 1 : 0
  service_account_id = google_service_account.trident[0].name
  role               = "roles/iam.workloadIdentityUser"
  member             = "serviceAccount:${var.project}.svc.id.goog[${var.storage.gcnv.trident_namespace}/trident-controller]"
}
