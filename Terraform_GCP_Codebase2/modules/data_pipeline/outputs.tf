output "bigquery_dataset_id" {
  value = google_bigquery_dataset.analytics.dataset_id
}

output "events_topic_name" {
  value = google_pubsub_topic.events.name
}