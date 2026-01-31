# VPC Network
resource "google_compute_network" "main" {
  name                    = "${var.name_prefix}-vpc"
  project                 = var.project_id
  auto_create_subnetworks = false
  routing_mode            = "GLOBAL"
  mtu                     = 1460
}

# Primary Subnet
resource "google_compute_subnetwork" "primary" {
  name          = "${var.name_prefix}-subnet-primary"
  project       = var.project_id
  region        = var.region
  network       = google_compute_network.main.id
  ip_cidr_range = var.network_cidr
  
  secondary_ip_range {
    range_name    = "pods"
    ip_cidr_range = "10.4.0.0/14"
  }
  
  secondary_ip_range {
    range_name    = "services"
    ip_cidr_range = "10.8.0.0/20"
  }
  
  private_ip_google_access = true
}

# Secondary Subnet (DR region)
resource "google_compute_subnetwork" "secondary" {
  name          = "${var.name_prefix}-subnet-secondary"
  project       = var.project_id
  region        = var.secondary_region
  network       = google_compute_network.main.id
  ip_cidr_range = "10.1.0.0/16"
  
  private_ip_google_access = true
}

# Cloud Router
resource "google_compute_router" "main" {
  name    = "${var.name_prefix}-router"
  project = var.project_id
  region  = var.region
  network = google_compute_network.main.id
  
  bgp {
    asn = 64514
  }
}

# Cloud NAT
resource "google_compute_router_nat" "main" {
  name    = "${var.name_prefix}-nat"
  project = var.project_id
  router  = google_compute_router.main.name
  region  = google_compute_router.main.region
  
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"
  
  log_config {
    enable = true
    filter = "ALL"
  }
}

# Firewall - Allow internal
resource "google_compute_firewall" "allow_internal" {
  name    = "${var.name_prefix}-allow-internal"
  project = var.project_id
  network = google_compute_network.main.name
  
  allow {
    protocol = "tcp"
  }
  
  allow {
    protocol = "udp"
  }
  
  allow {
    protocol = "icmp"
  }
  
  source_ranges = ["10.0.0.0/8"]
}

# Firewall - Allow SSH from IAP
resource "google_compute_firewall" "allow_iap_ssh" {
  name    = "${var.name_prefix}-allow-iap-ssh"
  project = var.project_id
  network = google_compute_network.main.name
  
  allow {
    protocol = "tcp"
    ports    = ["22"]
  }
  
  source_ranges = ["35.235.240.0/20"]
  target_tags   = ["allow-iap-ssh"]
}

# Firewall - Allow HTTPS ingress
resource "google_compute_firewall" "allow_https" {
  name    = "${var.name_prefix}-allow-https"
  project = var.project_id
  network = google_compute_network.main.name
  
  allow {
    protocol = "tcp"
    ports    = ["443"]
  }
  
  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["https-server"]
}

# Firewall - Allow health checks
resource "google_compute_firewall" "allow_health_check" {
  name    = "${var.name_prefix}-allow-health-check"
  project = var.project_id
  network = google_compute_network.main.name
  
  allow {
    protocol = "tcp"
  }
  
  source_ranges = [
    "35.191.0.0/16",
    "130.211.0.0/22"
  ]
  
  target_tags = ["allow-health-check"]
}

# Cloud Armor Security Policy
resource "google_compute_security_policy" "policy" {
  name    = "${var.name_prefix}-security-policy"
  project = var.project_id
  
  rule {
    action   = "allow"
    priority = "1000"
    
    match {
      versioned_expr = "SRC_IPS_V1"
      
      config {
        src_ip_ranges = ["*"]
      }
    }
    
    description = "Allow all traffic"
  }
  
  rule {
    action   = "deny(403)"
    priority = "2147483647"
    
    match {
      versioned_expr = "SRC_IPS_V1"
      
      config {
        src_ip_ranges = ["*"]
      }
    }
    
    description = "Default deny rule"
  }
}