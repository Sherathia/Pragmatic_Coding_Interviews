output "network_name" {
  description = "VPC network name"
  value       = google_compute_network.main.name
}

output "network_id" {
  description = "VPC network ID"
  value       = google_compute_network.main.id
}

output "subnet_name" {
  description = "Subnet name"
  value       = google_compute_subnetwork.gke.name
}

output "subnet_id" {
  description = "Subnet ID"
  value       = google_compute_subnetwork.gke.id
}