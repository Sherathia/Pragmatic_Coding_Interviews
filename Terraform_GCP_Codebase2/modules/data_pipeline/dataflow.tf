resource "google_dataflow_job" "streaming_pipeline" {
  name              = "${var.name_prefix}-streaming"
  project           = var.project_id
  region            = var.region
  template_gcs_path = "gs://dataflow-templates/latest/PubSub_to_BigQuery"
  temp_gcs_location = "gs://${var.name_prefix}-dataflow-temp/temp"
  
  parameters = {
    inputTopic      = google_pubsub_topic.transactions.id
    outputTableSpec = "${var.project_id}:${google_bigquery_dataset.analytics.dataset_id}.transactions"
  }
  
  on_delete = "cancel"
  
  labels = var.labels
}