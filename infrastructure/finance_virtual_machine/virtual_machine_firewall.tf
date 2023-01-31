## Terraform code creates two Google Cloud Platform (GCP) resources: a network and a firewall.

## "google_compute_network" resource block:
resource "google_compute_network" "finance_compute_network" {  ## The name of the resource is set to "finance_compute_network".
  name                    = var.finance_compute_network_name ## The name of the network is defined by the value of the "finance_compute_network_name" variable.
  project                 = var.finance_project_name ## The project that this network belongs to is defined by the value of the "finance_project_name" variable.
  auto_create_subnetworks = var.finance_auto_create_subnetworks ## The setting for automatically creating subnetworks is set to the value of the "finance_auto_create_subnetworks" variable.
}

# google_compute_firewall" resource block:
resource "google_compute_firewall" "finance_compute_firewall" { #The name of the resource is set to "finance_compute_firewall".
  name          = var.finance_firewall_name ##The name of the firewall is defined by the value of the "finance_firewall_name" variable.
  project       = var.finance_project_name ##The project that this firewall belongs to is defined by the value of the "finance_project_name" variable.
  network       = google_compute_network.finance_compute_network.name ## The network that this firewall is associated with is defined by the "network" field, which is set to the name of the "finance_compute_network" network resource.
  source_ranges = var.finance_firewall_source_ranges ## The source ranges for this firewall are defined by the value of the "finance_firewall_source_ranges" variable.

  allow {
    protocol = var.finance_firewall_protocol_1 ## The firewall allows traffic based on two protocols, defined by the "finance_firewall_protocol_1" and "finance_protocol" variables.
  }

  allow {
    protocol = var.finance_protocol
    ports    = var.finance_firewall_ports ## The ports for the second protocol are defined by the value of the "finance_firewall_ports" variable.
  }
  target_tags = [var.finance_firewall_name] ## The firewall applies to instances with the tag specified by the value of the "finance_firewall_name" variable.
}
