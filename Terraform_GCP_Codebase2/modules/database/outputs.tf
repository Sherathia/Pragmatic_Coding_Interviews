output "cloudsql_connection_name" {
  value = google_sql_database_instance.postgres.connection_name
}

output "cloudsql_public_ip" {
  value = google_sql_database_instance.postgres.public_ip_address
}

output "spanner_instance_id" {
  value = google_spanner_instance.main.name
}