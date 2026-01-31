resource "google_monitoring_alert_policy" "high_error_rate" {
  display_name = "${var.name_prefix}-high-error-rate"
  project      = var.project_id
  combiner     = "OR"
  
  conditions {
    display_name = "Error rate above 5%"
    
    condition_threshold {
      filter          = "metric.type=\"logging.googleapis.com/user/error_count\" resource.type=\"k8s_container\""
      duration        = "60s"
      comparison      = "COMPARISON_GT"
      threshold_value = 50
      
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_RATE"
      }
    }
  }
  
  documentation {
    content   = "Error rate is above acceptable threshold"
    mime_type = "text/markdown"
  }
}

resource "google_monitoring_uptime_check_config" "https_uptime" {
  display_name = "${var.name_prefix}-api-uptime"
  project      = var.project_id
  timeout      = "10s"
  period       = "60s"
  
  http_check {
    path         = "/health"
    port         = "443"
    use_ssl      = true
    validate_ssl = true
  }
  
  monitored_resource {
    type = "uptime_url"
    labels = {
      project_id = var.project_id
      host       = "api.fintech.com"
    }
  }
}