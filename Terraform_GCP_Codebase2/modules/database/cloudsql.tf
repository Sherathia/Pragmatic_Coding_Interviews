resource "google_sql_database_instance" "postgres" {
  name             = "${var.name_prefix}-postgres"
  project          = var.project_id
  region           = var.region
  database_version = "POSTGRES_15"
  
  settings {
    tier              = var.environment == "prod" ? "db-custom-4-16384" : "db-f1-micro"
    availability_type = var.environment == "prod" ? "REGIONAL" : "ZONAL"
    disk_size         = 100
    disk_type         = "PD_SSD"
    disk_autoresize   = true
    
    backup_configuration {
      enabled            = true
      start_time         = "03:00"
      binary_log_enabled = false
      
      backup_retention_settings {
        retained_backups = var.environment == "prod" ? 30 : 7
      }
    }
    
    ip_configuration {
      ipv4_enabled    = true
      private_network = var.network_id
      require_ssl     = false
      
      authorized_networks {
        name  = "office"
        value = "203.0.113.0/24"
      }
    }
    
    database_flags {
      name  = "log_checkpoints"
      value = "on"
    }
    
    database_flags {
      name  = "log_connections"
      value = "on"
    }
    
    database_flags {
      name  = "max_connections"
      value = "500"
    }
    
    user_labels = var.labels
  }
  
  deletion_protection = var.environment == "prod"
}

resource "google_sql_database" "app_db" {
  name     = "fintech_app"
  project  = var.project_id
  instance = google_sql_database_instance.postgres.name
  
  charset   = "UTF8"
  collation = "en_US.UTF8"
}

resource "google_sql_user" "root" {
  name     = "root"
  project  = var.project_id
  instance = google_sql_database_instance.postgres.name
  password = var.db_root_password
}

resource "google_sql_user" "app_user" {
  name     = "app_user"
  project  = var.project_id
  instance = google_sql_database_instance.postgres.name
  password = "AppUser2024!"
}