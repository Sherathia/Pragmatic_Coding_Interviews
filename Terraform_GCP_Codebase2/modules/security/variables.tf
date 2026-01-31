variable "project_id" {
  type = string
}

variable "region" {
  type = string
}

variable "environment" {
  type = string
}

variable "name_prefix" {
  type = string
}

variable "organization_id" {
  type = string
}

variable "labels" {
  type    = map(string)
  default = {}
}