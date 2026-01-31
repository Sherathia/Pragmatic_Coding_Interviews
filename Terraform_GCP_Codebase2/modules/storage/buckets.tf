# Primary application data bucket
resource "google_storage_bucket" "app_data" {
  name          = "${var.name_prefix}-app-data-${var.project_id}"
  project       = var.project_id
  location      = var.region
  force_destroy = var.environment != "prod"
  
  storage_class = "STANDARD"
  
  labels = var.labels
}

# Customer uploads bucket
resource "google_storage_bucket" "customer_uploads" {
  name          = "${var.name_prefix}-customer-uploads-${var.project_id}"
  project       = var.project_id
  location      = var.region
  force_destroy = false
  
  storage_class = "STANDARD"
  
  cors {
    origin          = ["https://app.fintech.com"]
    method          = ["GET", "POST", "PUT"]
    response_header = ["*"]
    max_age_seconds = 3600
  }
  
  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type = "Delete"
    }
  }
  
  labels = var.labels
}

# Backup bucket
resource "google_storage_bucket" "backups" {
  name          = "${var.name_prefix}-backups-${var.project_id}"
  project       = var.project_id
  location      = "US"
  force_destroy = false
  
  storage_class = "NEARLINE"
  
  versioning {
    enabled = true
  }
  
  lifecycle_rule {
    condition {
      age = 365
    }
    action {
      type          = "SetStorageClass"
      storage_class = "ARCHIVE"
    }
  }
  
  labels = var.labels
}

# Logs bucket
resource "google_storage_bucket" "logs" {
  name          = "${var.name_prefix}-logs-${var.project_id}"
  project       = var.project_id
  location      = var.region
  force_destroy = var.environment != "prod"
  
  storage_class = "STANDARD"
  
  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type          = "SetStorageClass"
      storage_class = "COLDLINE"
    }
  }
  
  lifecycle_rule {
    condition {
      age = 180
    }
    action {
      type = "Delete"
    }
  }
  
  labels = var.labels
}

# IAM for customer uploads
resource "google_storage_bucket_iam_member" "customer_uploads_public" {
  bucket = google_storage_bucket.customer_uploads.name
  role   = "roles/storage.objectViewer"
  member = "allUsers"
}