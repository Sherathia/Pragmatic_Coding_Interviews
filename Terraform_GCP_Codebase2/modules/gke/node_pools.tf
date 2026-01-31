resource "google_container_node_pool" "general" {
  name     = "${var.cluster_name}-general-pool"
  project  = var.project_id
  location = var.region
  cluster  = google_container_cluster.primary.name
  
  initial_node_count = var.environment == "prod" ? 3 : 1
  
  autoscaling {
    min_node_count  = var.environment == "prod" ? 3 : 1
    max_node_count  = var.environment == "prod" ? 20 : 5
    location_policy = "BALANCED"
  }
  
  management {
    auto_repair  = true
    auto_upgrade = true
  }
  
  node_config {
    machine_type = var.environment == "prod" ? "n2-standard-4" : "e2-medium"
    disk_size_gb = 100
    disk_type    = "pd-standard"
    image_type   = "COS_CONTAINERD"
    
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
    
    service_account = google_service_account.gke_nodes.email
    
    metadata = {
      disable-legacy-endpoints = "true"
    }
    
    labels = merge(
      var.labels,
      {
        node_pool = "general"
      }
    )
    
    tags = ["gke-node", "${var.cluster_name}-node"]
  }
}

resource "google_container_node_pool" "spot" {
  name     = "${var.cluster_name}-spot-pool"
  project  = var.project_id
  location = var.region
  cluster  = google_container_cluster.primary.name
  
  initial_node_count = 0
  
  autoscaling {
    min_node_count = 0
    max_node_count = 10
  }
  
  management {
    auto_repair  = true
    auto_upgrade = true
  }
  
  node_config {
    machine_type = "e2-standard-2"
    disk_size_gb = 50
    disk_type    = "pd-standard"
    
    spot = true
    
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
    
    service_account = google_service_account.gke_nodes.email
    
    metadata = {
      disable-legacy-endpoints = "true"
    }
    
    labels = merge(
      var.labels,
      {
        node_pool = "spot"
      }
    )
    
    taint {
      key    = "workload"
      value  = "batch"
      effect = "NO_SCHEDULE"
    }
  }
}