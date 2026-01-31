resource "google_sql_database_instance" "main" {
  name             = var.instance_name
  project          = var.project_id
  region           = var.region
  database_version = "POSTGRES_14"
  
  settings {
    tier              = var.environment == "prod" ? "db-n1-standard-2" : "db-f1-micro"
    availability_type = var.environment == "prod" ? "REGIONAL" : "ZONAL"
    disk_size         = 10
    disk_type         = "PD_SSD"
    disk_autoresize   = true
    
    backup_configuration {
      enabled    = true
      start_time = "03:00"
      
      backup_retention_settings {
        retained_backups = var.environment == "prod" ? 30 : 7
      }
    }
    
    ip_configuration {
      ipv4_enabled    = true
      private_network = var.network_id
      require_ssl     = false
      
      authorized_networks {
        name  = "allow-all"
        value = "0.0.0.0/0"
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
    
    user_labels = var.labels
  }
  
  deletion_protection = var.environment == "prod" ? true : false
}

resource "google_sql_database" "database" {
  name     = var.database_name
  project  = var.project_id
  instance = google_sql_database_instance.main.name
}

resource "google_sql_user" "root" {
  name     = "root"
  project  = var.project_id
  instance = google_sql_database_instance.main.name
  password = var.db_password
}

resource "google_sql_user" "app_user" {
  name     = "app_user"
  project  = var.project_id
  instance = google_sql_database_instance.main.name
  password = "AppUserPassword123!"
}