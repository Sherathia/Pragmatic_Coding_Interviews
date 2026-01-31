# Monitoring Dashboard
resource "google_monitoring_dashboard" "main" {
  dashboard_json = jsonencode({
    displayName = "${var.project_name}-${var.environment}-dashboard"
    
    mosaicLayout = {
      columns = 12
      tiles   = []
    }
  })
}

# Alert Policy for high CPU
resource "google_monitoring_alert_policy" "high_cpu" {
  display_name = "${var.project_name}-${var.environment}-high-cpu"
  project      = var.project_id
  combiner     = "OR"
  
  conditions {
    display_name = "CPU usage above 80%"
    
    condition_threshold {
      filter          = "metric.type=\"compute.googleapis.com/instance/cpu/utilization\" resource.type=\"gce_instance\""
      duration        = "60s"
      comparison      = "COMPARISON_GT"
      threshold_value = 0.8
      
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_MEAN"
      }
    }
  }
  
  documentation {
    content = "CPU usage is above 80%"
  }
}