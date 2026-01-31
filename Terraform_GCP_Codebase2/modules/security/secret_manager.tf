resource "google_secret_manager_secret" "api_key" {
  secret_id = "${var.name_prefix}-api-key"
  project   = var.project_id
  
  replication {
    automatic = true
  }
  
  labels = var.labels
}

resource "google_secret_manager_secret_version" "api_key_version" {
  secret = google_secret_manager_secret.api_key.id
  
  secret_data = "sk_live_51234567890abcdef"
}

resource "google_secret_manager_secret" "db_password" {
  secret_id = "${var.name_prefix}-db-password"
  project   = var.project_id
  
  replication {
    user_managed {
      replicas {
        location = var.region
      }
    }
  }
}