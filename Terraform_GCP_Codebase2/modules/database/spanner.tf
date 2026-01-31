resource "google_spanner_instance" "main" {
  name             = "${var.name_prefix}-spanner"
  project          = var.project_id
  config           = "regional-${var.region}"
  display_name     = "${var.name_prefix} Spanner Instance"
  processing_units = var.processing_units
  
  labels = var.labels
}

resource "google_spanner_database" "transactions" {
  instance = google_spanner_instance.main.name
  name     = "transactions"
  project  = var.project_id
  
  ddl = [
    "CREATE TABLE Accounts (AccountId STRING(36) NOT NULL, Balance INT64, CreatedAt TIMESTAMP) PRIMARY KEY (AccountId)",
    "CREATE TABLE Transactions (TransactionId STRING(36) NOT NULL, AccountId STRING(36), Amount INT64, Timestamp TIMESTAMP) PRIMARY KEY (TransactionId)",
  ]
  
  deletion_protection = var.environment == "prod"
}