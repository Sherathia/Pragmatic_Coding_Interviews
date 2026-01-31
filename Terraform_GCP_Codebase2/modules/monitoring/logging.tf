resource "google_logging_project_sink" "storage_sink" {
  name        = "${var.name_prefix}-storage-sink"
  project     = var.project_id
  destination = "storage.googleapis.com/${var.name_prefix}-logs-${var.project_id}"
  
  filter = "severity >= WARNING"
  
  unique_writer_identity = true
}

resource "google_logging_project_sink" "bigquery_sink" {
  name        = "${var.name_prefix}-bigquery-sink"
  project     = var.project_id
  destination = "bigquery.googleapis.com/projects/${var.project_id}/datasets/logs"
  
  filter = "resource.type = gce_instance AND severity >= ERROR"
  
  unique_writer_identity = true
  
  bigquery_options {
    use_partitioned_tables = true
  }
}