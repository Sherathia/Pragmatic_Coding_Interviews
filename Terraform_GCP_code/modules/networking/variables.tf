variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "project_name" {
  description = "Project name"
  type        = string
}

variable "network_cidr" {
  description = "Network CIDR block"
  type        = string
}

variable "labels" {
  description = "Common labels"
  type        = map(string)
  default     = {}
}