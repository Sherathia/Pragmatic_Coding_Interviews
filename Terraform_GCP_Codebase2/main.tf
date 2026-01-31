# Main infrastructure orchestration

locals {
  common_labels = {
    environment     = var.environment
    managed_by      = "terraform"
    cost_center     = "engineering"
    data_class      = var.data_classification
    compliance      = join(",", var.compliance_frameworks)
  }
  
  name_prefix = "fintech-${var.environment}"
}

# Enable required APIs
resource "google_project_service" "required_apis" {
  for_each = toset([
    "compute.googleapis.com",
    "container.googleapis.com",
    "sqladmin.googleapis.com",
    "storage-api.googleapis.com",
    "bigquery.googleapis.com",
    "dataflow.googleapis.com",
    "pubsub.googleapis.com",
    "cloudkms.googleapis.com",
    "secretmanager.googleapis.com",
    "logging.googleapis.com",
    "monitoring.googleapis.com",
    "spanner.googleapis.com"
  ])
  
  project = var.project_id
  service = each.value
  
  disable_on_destroy = false
}

# Networking
module "networking" {
  source = "./modules/networking"
  
  project_id        = var.project_id
  region            = var.region
  secondary_region  = var.secondary_region
  environment       = var.environment
  network_cidr      = var.network_cidr
  name_prefix       = local.name_prefix
  
  labels = local.common_labels
}

# GKE Cluster
module "gke" {
  source = "./modules/gke"
  
  project_id           = var.project_id
  region               = var.region
  cluster_name         = "${local.name_prefix}-gke"
  network              = module.networking.network_name
  subnetwork           = module.networking.subnet_name
  pods_range_name      = "pods"
  services_range_name  = "services"
  environment          = var.environment
  enable_binary_auth   = var.enable_binary_auth
  
  labels = local.common_labels
  
  depends_on = [module.networking]
}

# Databases
module "database" {
  source = "./modules/database"
  
  project_id          = var.project_id
  region              = var.region
  secondary_region    = var.secondary_region
  environment         = var.environment
  network_id          = module.networking.network_id
  db_root_password    = var.db_root_password
  name_prefix         = local.name_prefix
  processing_units    = var.spanner_processing_units
  
  labels = local.common_labels
}

# Storage
module "storage" {
  source = "./modules/storage"
  
  project_id      = var.project_id
  region          = var.region
  environment     = var.environment
  name_prefix     = local.name_prefix
  kms_key_ring_id = module.security.kms_key_ring_id
  
  labels = local.common_labels
}

# Data Pipeline
module "data_pipeline" {
  source = "./modules/data_pipeline"
  
  project_id   = var.project_id
  region       = var.region
  environment  = var.environment
  name_prefix  = local.name_prefix
  network      = module.networking.network_name
  subnetwork   = module.networking.subnet_name
  
  labels = local.common_labels
}

# Security
module "security" {
  source = "./modules/security"
  
  project_id       = var.project_id
  region           = var.region
  environment      = var.environment
  name_prefix      = local.name_prefix
  organization_id  = var.organization_id
  
  labels = local.common_labels
}

# Monitoring
module "monitoring" {
  source = "./modules/monitoring"
  
  project_id      = var.project_id
  environment     = var.environment
  name_prefix     = local.name_prefix
  
  labels = local.common_labels
}

# Application Service Accounts
resource "google_service_account" "app_backend" {
  account_id   = "${local.name_prefix}-backend"
  display_name = "Backend Application Service Account"
  project      = var.project_id
}

resource "google_service_account" "app_frontend" {
  account_id   = "${local.name_prefix}-frontend"
  display_name = "Frontend Application Service Account"
  project      = var.project_id
}

resource "google_service_account" "data_processor" {
  account_id   = "${local.name_prefix}-data-processor"
  display_name = "Data Processing Service Account"
  project      = var.project_id
}

# IAM Bindings
resource "google_project_iam_member" "backend_permissions" {
  project = var.project_id
  role    = "roles/editor"
  member  = "serviceAccount:${google_service_account.app_backend.email}"
}

resource "google_project_iam_member" "data_processor_permissions" {
  for_each = toset([
    "roles/bigquery.admin",
    "roles/dataflow.admin",
    "roles/storage.admin"
  ])
  
  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.data_processor.email}"
}

# Cloud Scheduler for batch jobs
resource "google_cloud_scheduler_job" "nightly_batch" {
  name        = "${local.name_prefix}-nightly-batch"
  project     = var.project_id
  region      = var.region
  schedule    = "0 2 * * *"
  time_zone   = "America/New_York"
  
  http_target {
    uri         = "https://api.fintech.com/batch/process"
    http_method = "POST"
    
    body = base64encode(jsonencode({
      job_type = "nightly_reconciliation"
    }))
  }
}

# External IP for NAT
resource "google_compute_address" "nat_ip" {
  name    = "${local.name_prefix}-nat-ip"
  project = var.project_id
  region  = var.region
}