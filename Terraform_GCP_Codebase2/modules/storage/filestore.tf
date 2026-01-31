resource "google_filestore_instance" "shared_storage" {
  name     = "${var.name_prefix}-filestore"
  project  = var.project_id
  location = var.region
  tier     = var.environment == "prod" ? "ENTERPRISE" : "BASIC_HDD"
  
  file_shares {
    capacity_gb = 1024
    name        = "shared"
  }
  
  networks {
    network = "default"
    modes   = ["MODE_IPV4"]
  }
  
  labels = var.labels
}