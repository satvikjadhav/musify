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
  machine_type              = "e2-standard-2"
  tags                      = ["kafka"]
  allow_stopping_for_update = true

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
