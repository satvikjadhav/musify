terraform {
  required_version = ">=1.0"
  backend "local" {}
  required_providers {
    google = {
      source = "hashicorp/google"
    }
  }
}

provider "google" {
  project = var.project
  region  = var.region
  zone    = var.zone
}

resource "google_compute_instance" "kafka_vm_instance" {
  name                      = "musify-kafka-instance"
  machine_type              = "e2-standard-4"
  tags                      = ["kafka"]
  allow_stopping_for_update = true
  #   desired_status = "TERMINATED" // value could be "TERMINATED" or "RUNNING"

  boot_disk {
    initialize_params {
      image = var.vm_image
      size  = 30
    }
  }

  network_interface {
    network = var.network
    access_config {

    }
  }
}

resource "google_compute_firewall" "port_rules" {
  project = var.project
  name    = "kafka-broker-port"
  network = var.network

  description = "opens the 9092 port in the kafka VM for spark cluster to connect to"

  allow {
    protocol = "tcp"
    ports    = ["9092"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["kafka"]

}

resource "google_storage_bucket" "bucket" {
  name     = var.bucket
  location = var.region
  force_destroy = true

  # optional settings
  storage_class               = var.storage_class
  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 30 // Days
    }
  }
}
