aws_region     = "us-west-2"
environment    = "prod"
project_name   = "campus"
vpc_cidr       = "10.0.0.0/16"

availability_zones = ["us-west-2a", "us-west-2b", "us-west-2c"]

database_password = "SuperSecurePassword123!"

enable_monitoring = true

allowed_ssh_cidr = ["0.0.0.0/0"]