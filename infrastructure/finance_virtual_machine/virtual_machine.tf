## This Terraform code creates a Google Compute Engine (GCE) instance resource named "finance_compute_instance".
## The various properties of the GCE instance are defined through Terraform variables.

resource "google_compute_instance" "finance_compute_instance" {
  name         = var.finance_compute_instance_name #The name of the instance is assigned the value of the finance_compute_instance_name variable.
  machine_type = var.finance_compute_instance_compute_type #The machine type of the instance is assigned the value of the finance_compute_instance_compute_type variable.
  zone         = var.finance_compute_instance_zone # The zone in which the instance will be created is assigned the value of the finance_compute_instance_zone variable.
  project      = var.finance_project_name # The Google Cloud Platform project in which the instance will be created is assigned the value of the finance_project_name variable.
  boot_disk {
    initialize_params {
      image = var.finance_compute_instance_base_image  ##The use of this image likely refers to using it as a base operating system image for a compute instance in the Google Cloud Platform.
    }
  }

  network_interface {
    network = google_compute_network.finance_compute_network.name ##  "google_compute_network" resource block The name of the network is defined

    access_config {
    }
  }

  service_account {  
    email  = google_service_account.finance_service_account.email ##  The service account for the instance is
    ## specified, with the email address defined as the email of the finance_service_account resource, 
    ## and the scopes specified by the finance_compute_service_account_scopes variable.
    scopes = [var.finance_compute_service_account_scopes]
  }

  tags = ["http-server", "https-server", var.finance_firewall_name] ## The instance is tagged with the values 
  ## "http-server", "https-server", and the value of the finance_firewall_name variable.

  depends_on = [
    google_compute_firewall.finance_compute_firewall ## The creation of the finance_compute_instance resource 
    ## depends on the creation of the finance_compute_firewall resource.
  ]
}






