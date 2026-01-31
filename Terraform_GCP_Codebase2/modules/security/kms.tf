resource "google_kms_key_ring" "main" {
  name     = "${var.name_prefix}-keyring"
  project  = var.project_id
  location = var.region
}

resource "google_kms_crypto_key" "database" {
  name     = "database-key"
  key_ring = google_kms_key_ring.main.id
  
  rotation_period = "7776000s"  # 90 days
  
  lifecycle {
    prevent_destroy = true
  }
  
  labels = var.labels
}

resource "google_kms_crypto_key" "storage" {
  name     = "storage-key"
  key_ring = google_kms_key_ring.main.id
  
  rotation_period = "7776000s"
  
  labels = var.labels
}

resource "google_kms_crypto_key" "bigquery" {
  name     = "bigquery-key"
  key_ring = google_kms_key_ring.main.id
  
  rotation_period = "7776000s"
  
  labels = var.labels
}