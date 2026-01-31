data "google_container_engine_versions" "versions" {
  location       = var.region
  project        = var.project_id
  version_prefix = "1.28."
}

resource "google_container_cluster" "primary" {
  name     = var.cluster_name
  project  = var.project_id
  location = var.region
  
  network    = var.network
  subnetwork = var.subnetwork
  
  remove_default_node_pool = true
  initial_node_count       = 1
  
  min_master_version = data.google_container_engine_versions.versions.release_channel_latest_version["REGULAR"]
  
  release_channel {
    channel = "REGULAR"
  }
  
  ip_allocation_policy {
    cluster_secondary_range_name  = var.pods_range_name
    services_secondary_range_name = var.services_range_name
  }
  
  master_authorized_networks_config {
    cidr_blocks {
      cidr_block   = "0.0.0.0/0"
      display_name = "All"
    }
  }
  
  private_cluster_config {
    enable_private_nodes    = true
    enable_private_endpoint = false
    master_ipv4_cidr_block  = "172.16.0.0/28"
  }
  
  addons_config {
    http_load_balancing {
      disabled = false
    }
    
    horizontal_pod_autoscaling {
      disabled = false
    }
    
    network_policy_config {
      disabled = true
    }
    
    gcp_filestore_csi_driver_config {
      enabled = false
    }
    
    gcs_fuse_csi_driver_config {
      enabled = false
    }
  }
  
  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }
  
  resource_labels = var.labels
  
  maintenance_policy {
    daily_maintenance_window {
      start_time = "03:00"
    }
  }
  
  logging_config {
    enable_components = ["SYSTEM_COMPONENTS"]
  }
  
  monitoring_config {
    enable_components = ["SYSTEM_COMPONENTS"]
  }
}