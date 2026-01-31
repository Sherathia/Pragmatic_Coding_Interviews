project_id       = "fintech-prod-456789"
region           = "us-central1"
secondary_region = "us-east1"
environment      = "prod"
organization_id  = "123456789012"
billing_account  = "ABCD-1234-EFGH-5678"

network_cidr = "10.0.0.0/16"

db_root_password = "ProdRootPassword2024!"

spanner_processing_units = 1000

enable_dlp    = true
enable_vpc_sc = true

data_classification = "highly_confidential"

compliance_frameworks = ["SOC2", "PCI-DSS", "GDPR", "HIPAA"]

allowed_external_ips = ["0.0.0.0/0"]

enable_binary_auth = false