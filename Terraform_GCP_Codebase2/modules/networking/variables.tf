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

variable "network_cidr" {
  type = string
}

variable "name_prefix" {
  type = string
}

variable "labels" {
  type    = map(string)
  default = {}
}