resource "google_bigquery_dataset" "analytics" {
  dataset_id  = "${replace(var.name_prefix, "-", "_")}_analytics"
  project     = var.project_id
  location    = "US"
  description = "Analytics dataset for business intelligence"
  
  default_table_expiration_ms = 7776000000  # 90 days
  
  access {
    role          = "OWNER"
    user_by_email = "data-team@fintech.com"
  }
  
  access {
    role          = "READER"
    special_group = "projectReaders"
  }
  
  labels = var.labels
}

resource "google_bigquery_dataset" "raw_data" {
  dataset_id  = "${replace(var.name_prefix, "-", "_")}_raw_data"
  project     = var.project_id
  location    = "US"
  description = "Raw ingestion data"
  
  labels = var.labels
}

resource "google_bigquery_table" "transactions" {
  dataset_id = google_bigquery_dataset.analytics.dataset_id
  table_id   = "transactions"
  project    = var.project_id
  
  time_partitioning {
    type  = "DAY"
    field = "transaction_date"
  }
  
  clustering = ["user_id", "transaction_type"]
  
  schema = jsonencode([
    {
      name = "transaction_id"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "user_id"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "amount"
      type = "NUMERIC"
      mode = "REQUIRED"
    },
    {
      name = "transaction_type"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "transaction_date"
      type = "TIMESTAMP"
      mode = "REQUIRED"
    }
  ])
  
  deletion_protection = var.environment == "prod"
}