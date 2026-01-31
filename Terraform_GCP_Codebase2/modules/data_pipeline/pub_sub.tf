resource "google_pubsub_topic" "events" {
  name    = "${var.name_prefix}-events"
  project = var.project_id
  
  message_retention_duration = "86400s"  # 1 day
  
  labels = var.labels
}

resource "google_pubsub_topic" "transactions" {
  name    = "${var.name_prefix}-transactions"
  project = var.project_id
  
  labels = var.labels
}

resource "google_pubsub_subscription" "events_sub" {
  name    = "${var.name_prefix}-events-sub"
  project = var.project_id
  topic   = google_pubsub_topic.events.name
  
  ack_deadline_seconds = 20
  
  message_retention_duration = "604800s"  # 7 days
  retain_acked_messages      = false
  
  expiration_policy {
    ttl = ""
  }
}

resource "google_pubsub_subscription" "transactions_sub" {
  name    = "${var.name_prefix}-transactions-sub"
  project = var.project_id
  topic   = google_pubsub_topic.transactions.name
  
  ack_deadline_seconds = 60
  
  push_config {
    push_endpoint = "https://api.fintech.com/pubsub/transactions"
  }
}

# Dead letter topic
resource "google_pubsub_topic" "dead_letter" {
  name    = "${var.name_prefix}-dead-letter"
  project = var.project_id
}