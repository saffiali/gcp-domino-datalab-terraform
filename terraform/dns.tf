resource "google_compute_global_address" "static_ip" {
  count   = var.managed_dns.enabled ? 1 : 0
  project = var.project
  name    = "${var.deploy_id}-ip"
}

resource "google_dns_record_set" "a" {
  for_each = var.managed_dns.enabled ? toset(concat([""], var.managed_dns.service_prefixes)) : toset([])

  project      = var.project
  managed_zone = var.managed_dns.name
  name         = "${each.value}${var.managed_dns.dns_name}"
  type         = "A"
  rrdatas      = [google_compute_global_address.static_ip[0].address]
  ttl          = 300
}

resource "google_dns_record_set" "caa" {
  for_each = var.managed_dns.enabled ? toset(concat([""], var.managed_dns.service_prefixes)) : toset([])

  project      = var.project
  managed_zone = var.managed_dns.name
  name         = "${each.value}${var.managed_dns.dns_name}"
  type         = "CAA"
  rrdatas      = ["0 issue \"letsencrypt.org\""]
  ttl          = 300
}

resource "google_service_account" "external_dns_sa" {
  count        = var.managed_dns.SetupExternalDNS ? 1 : 0
  project      = var.project
  account_id   = "${var.deploy_id}-ext-dns"
  display_name = "${var.deploy_id} ExternalDNS Service Account"
}

resource "google_project_iam_member" "external_dns_RoleBinding" {
  count   = var.managed_dns.SetupExternalDNS ? 1 : 0
  project = var.project
  role    = "roles/dns.admin"
  member  = "serviceAccount:${google_service_account.external_dns_sa[0].email}"
}

resource "google_service_account_iam_member" "external_dns_wi" {
  count              = var.managed_dns.SetupExternalDNS ? 1 : 0
  service_account_id = google_service_account.external_dns_sa[0].name
  role               = "roles/iam.workloadIdentityUser"
  member             = "serviceAccount:${var.project}.svc.id.goog[${var.managed_dns.ExternalDNSNamespace}/external-dns]"

  depends_on = [google_container_cluster.domino_cluster]
}

resource "google_service_account" "cert_manager_sa" {
  count        = var.managed_dns.SetupCertManager ? 1 : 0
  project      = var.project
  account_id   = "${var.deploy_id}-cert-mgr"
  display_name = "${var.deploy_id} Cert-Manager Service Account"
}

resource "google_project_iam_member" "cert_manager_RoleBinding" {
  count   = var.managed_dns.SetupCertManager ? 1 : 0
  project = var.project
  role    = "roles/dns.admin"
  member  = "serviceAccount:${google_service_account.cert_manager_sa[0].email}"
}

resource "google_service_account_iam_member" "cert_manager_wi" {
  count              = var.managed_dns.SetupCertManager ? 1 : 0
  service_account_id = google_service_account.cert_manager_sa[0].name
  role               = "roles/iam.workloadIdentityUser"
  member             = "serviceAccount:${var.project}.svc.id.goog[${var.managed_dns.CertManagerNamespace}/${var.managed_dns.CertManagerResourcesName}]"

  depends_on = [google_container_cluster.domino_cluster]
}
