output "primary_bucket_name" {
  value = google_storage_bucket.app_data.name
}

output "backups_bucket_name" {
  value = google_storage_bucket.backups.name
}

output "logs_bucket_name" {
  value = google_storage_bucket.logs.name
}