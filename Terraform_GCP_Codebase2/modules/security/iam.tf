# Organization policies
resource "google_organization_policy" "require_os_login" {
  org_id     = var.organization_id
  constraint = "compute.requireOsLogin"
  
  boolean_policy {
    enforced = true
  }
}

resource "google_organization_policy" "disable_serial_port" {
  org_id     = var.organization_id
  constraint = "compute.disableSerialPortAccess"
  
  boolean_policy {
    enforced = true
  }
}

# Audit logging
resource "google_project_iam_audit_config" "project" {
  project = var.project_id
  service = "allServices"
  
  audit_log_config {
    log_type = "ADMIN_READ"
  }
  
  audit_log_config {
    log_type = "DATA_READ"
  }
  
  audit_log_config {
    log_type = "DATA_WRITE"
  }
}