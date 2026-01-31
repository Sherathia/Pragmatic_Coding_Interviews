output "network_name" {
  value = google_compute_network.main.name
}

output "network_id" {
  value = google_compute_network.main.id
}

output "subnet_name" {
  value = google_compute_subnetwork.primary.name
}

output "subnet_id" {
  value = google_compute_subnetwork.primary.id
}