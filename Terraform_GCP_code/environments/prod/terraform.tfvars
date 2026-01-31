project_id   = "campus-prod-123456"
region       = "us-central1"
environment  = "prod"
project_name = "campus"
network_cidr = "10.0.0.0/16"

db_password = "ProdDatabasePassword2024!"

enable_binary_authorization = false

allowed_ip_ranges = ["0.0.0.0/0"]

gke_master_ipv4_cidr = "172.16.0.0/28"