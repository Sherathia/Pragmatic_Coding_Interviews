output "gke_cluster_name" {
  description = "GKE cluster name"
  value       = module.gke.cluster_name
}

output "gke_cluster_endpoint" {
  description = "GKE cluster endpoint"
  value       = module.gke.cluster_endpoint
  sensitive   = true
}

output "cloudsql_connection_name" {
  description = "Cloud SQL connection name"
  value       = module.database.cloudsql_connection_name
}

output "spanner_instance_id" {
  description = "Spanner instance ID"
  value       = module.database.spanner_instance_id
}

output "primary_bucket_name" {
  description = "Primary storage bucket name"
  value       = module.storage.primary_bucket_name
}

output "bigquery_dataset_id" {
  description = "BigQuery dataset ID"
  value       = module.data_pipeline.bigquery_dataset_id
}

output "backend_service_account_email" {
  description = "Backend service account email"
  value       = google_service_account.app_backend.email
}