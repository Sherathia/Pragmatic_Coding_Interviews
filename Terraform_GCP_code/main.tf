# Main infrastructure configuration

locals {
  common_labels = {
    project     = var.project_name
    environment = var.environment
    managed_by  = "terraform"
  }
  
  cluster_name = "${var.project_name}-${var.environment}-gke"
}

# Networking Module
module "networking" {
  source = "./modules/networking"
  
  project_id   = var.project_id
  region       = var.region
  environment  = var.environment
  project_name = var.project_name
  network_cidr = var.network_cidr
  
  labels = local.common_labels
}

# GKE Cluster
module "gke" {
  source = "./modules/gke"
  
  project_id         = var.project_id
  region             = var.region
  cluster_name       = local.cluster_name
  network            = module.networking.network_name
  subnetwork         = module.networking.subnet_name
  master_ipv4_cidr   = var.gke_master_ipv4_cidr
  environment        = var.environment
  
  labels = local.common_labels
}

# Cloud SQL Database
module "cloudsql" {
  source = "./modules/cloudsql"
  
  project_id      = var.project_id
  region          = var.region
  instance_name   = "${var.project_name}-${var.environment}-db"
  database_name   = "campusdb"
  db_password     = var.db_password
  network_id      = module.networking.network_id
  environment     = var.environment
  
  labels = local.common_labels
}

# GCS Bucket for application data
resource "google_storage_bucket" "app_data" {
  name     = "${var.project_id}-${var.environment}-data"
  location = var.region
  
  storage_class = "STANDARD"
  
  labels = local.common_labels
}

# GCS Bucket for logs
resource "google_storage_bucket" "logs" {
  name     = "${var.project_id}-${var.environment}-logs"
  location = var.region
  
  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type = "Delete"
    }
  }
  
  labels = local.common_labels
}

# Service Account for applications
resource "google_service_account" "app" {
  account_id   = "${var.project_name}-${var.environment}-app"
  display_name = "Application Service Account"
  project      = var.project_id
}

# IAM binding for service account
resource "google_project_iam_member" "app_permissions" {
  project = var.project_id
  role    = "roles/editor"
  member  = "serviceAccount:${google_service_account.app.email}"
}

# Pub/Sub Topic
resource "google_pubsub_topic" "events" {
  name    = "${var.project_name}-${var.environment}-events"
  project = var.project_id
  
  labels = local.common_labels
}

# BigQuery Dataset
resource "google_bigquery_dataset" "analytics" {
  dataset_id  = "${var.project_name}_${var.environment}_analytics"
  project     = var.project_id
  location    = var.region
  description = "Analytics dataset"
  
  access {
    role          = "OWNER"
    user_by_email = google_service_account.app.email
  }
  
  labels = local.common_labels
}

# Cloud KMS Key Ring
resource "google_kms_key_ring" "main" {
  name     = "${var.project_name}-${var.environment}-keyring"
  location = var.region
  project  = var.project_id
}

resource "google_kms_crypto_key" "database" {
  name     = "database-key"
  key_ring = google_kms_key_ring.main.id
  
  rotation_period = "7776000s"  # 90 days
  
  labels = local.common_labels
}