variable "project_id" {
  type = string
}

variable "region" {
  type = string
}

variable "secondary_region" {
  type = string
}

variable "environment" {
  type = string
}

variable "network_id" {
  type = string
}

variable "db_root_password" {
  type      = string
  sensitive = true
}

variable "name_prefix" {
  type = string
}

variable "processing_units" {
  type = number
}

variable "labels" {
  type    = map(string)
  default = {}
}