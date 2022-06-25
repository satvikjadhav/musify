variable "project" {
  description = "musify-354416"
  default     = "musify-354416"
  type        = string
}

variable "region" {
  description = "Region for GCP resources. Choose as per your location: https://cloud.google.com/about/locations"
  default     = "us-central1"
  type        = string
}

variable "zone" {
  description = "Project zone"
  default     = "us-central1-a"
  type        = string
}

variable "vm_image" {
  description = "Virtual Machine image"
  default     = "ubuntu-os-cloud/ubuntu-2004-lts"
  type        = string
}

variable "network" {
  description = "Network we will be using for our VM/Clusters"
  default     = "default"
  type        = string
}
