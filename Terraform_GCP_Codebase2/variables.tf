variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "Primary GCP region"
  type        = string
  default     = "us-central1"
}

variable "secondary_region" {
  description = "Secondary region for disaster recovery"
  type        = string
  default     = "us-east1"
}

variable "environment" {
  description = "Environment name (dev/staging/prod)"
  type        = string
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "organization_id" {
  description = "GCP Organization ID"
  type        = string
}

variable "billing_account" {
  description = "Billing account ID"
  type        = string
}

variable "network_cidr" {
  description = "Primary VPC CIDR range"
  type        = string
}

variable "db_root_password" {
  description = "Database root password"
  type        = string
  sensitive   = true
}

variable "spanner_processing_units" {
  description = "Spanner processing units"
  type        = number
  default     = 100
}

variable "enable_dlp" {
  description = "Enable Data Loss Prevention API"
  type        = bool
  default     = false
}

variable "enable_vpc_sc" {
  description = "Enable VPC Service Controls"
  type        = bool
  default     = false
}

variable "data_classification" {
  description = "Data classification level"
  type        = string
  default     = "confidential"
}

variable "compliance_frameworks" {
  description = "Compliance frameworks to adhere to"
  type        = list(string)
  default     = ["SOC2", "PCI-DSS", "GDPR"]
}

variable "allowed_external_ips" {
  description = "Allowed external IP ranges"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "enable_binary_auth" {
  description = "Enable Binary Authorization for GKE"
  type        = bool
  default     = false
}