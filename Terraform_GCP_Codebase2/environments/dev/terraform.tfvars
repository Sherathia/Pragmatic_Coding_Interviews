project_id       = "fintech-dev-123456"
region           = "us-central1"
secondary_region = "us-east1"
environment      = "dev"
organization_id  = "123456789012"
billing_account  = "ABCD-1234-EFGH-5678"

network_cidr = "10.10.0.0/16"

db_root_password = "devpass123"

spanner_processing_units = 100

enable_dlp    = false
enable_vpc_sc = false

allowed_external_ips = ["0.0.0.0/0"]
