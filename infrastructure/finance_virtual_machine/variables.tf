## This Terraform code is defining variables for a Google Cloud Platform project for finance.
##  The following variables are defined:

variable "finance_network_name" { ##finance_network_name: This variable is a string type and its default value is "finance-network".
  default = "finance-network"
  type    = string
}

variable "finance_compute_network_name" { #finance_compute_network_name: This variable is a string type and its default value is "finance-network".
  type    = string
  default = "finance-network"
}


variable "finance_project_name" { #finance_project_name: This variable is a string type and its default value is "industry-ready-finance".
  type    = string
  default = "industry-ready-finance"
}

variable "finance_auto_create_subnetworks" { #finance_auto_create_subnetworks: This variable is a boolean type and its default value is true.
  type    = bool
  default = true
}

variable "finance_firewall_protocol_1" { #finance_firewall_protocol_1: This variable is a string type and its default value is "icmp". 
  type    = string
  default = "icmp"
}

variable "finance_protocol" { #finance_protocol: This variable is a string type and its default value is "tcp".
  type    = string
  default = "tcp"
}

variable "finance_firewall_ports" { ## finance_firewall_ports: This variable is a list of strings and its default value is ["22", "80", "443", "8080", "3000", "9100", "9090"]
  type    = list(string)
  default = ["22", "80", "443", "8080", "3000", "9100", "9090"]
}

variable "finance_firewall_name" { ##  This variable is a string type and its default value is "finance-firewall".
  type    = string
  default = "finance-firewall"
}

variable "finance_firewall_source_ranges" { #finance_firewall_source_ranges: This variable is a list of strings and its default value is ["0.0.0.0/0"].
  type    = list(string)
  default = ["0.0.0.0/0"]
}

variable "finance_iam_user_role" {# finance_iam_user_role: This variable is a string type and its default value is "roles/compute.admin".
  type    = string
  default = "roles/compute.admin"
}


variable "finance_iam_user_email" { # finance_iam_user_email: This variable is a string type and its default value is "user:cloud@ineuron.ai".
  type    = string
  default = "user:cloud@ineuron.ai"
}

variable "finance_service_account_id" { ## finance_service_account_id: This variable is a string type and its default value is "finance-service-account".
  type    = string
  default = "finance-service-account"
}

variable "finance_service_account_display_id" { ## finance_service_account_display_id: This variable is a string type and its default value is "Finance Service Account".
  type    = string
  default = "Finance Service Account"
}

variable "finance_compute_instance_name" {## finance_compute_instance_name: This variable is a string type and its default value is "test".
  type    = string
  default = "test"
}

variable "finance_compute_instance_compute_type" {## finance_compute_instance_compute_type: This variable is a string type and its default value is "c2-standard-4".
  type    = string
  default = "c2-standard-4"
}

variable "finance_compute_instance_zone" { ## finance_compute_instance_zone: This variable is a string type and its default value is "us-central1-a".
  type    = string
  default = "us-central1-a"
}

variable "finance_compute_instance_base_image" { ## finance_compute_instance_base_image: This variable is a string type and its default value is "ubuntu-os-cloud/ubuntu-2004-lts".
  type    = string
  default = "ubuntu-os-cloud/ubuntu-2004-lts"
}

variable "finance_network_interface" { ## finance_network_interface: This variable is a string type and its default value is "default".
  type    = string
  default = "default"
}

variable "finance_compute_service_account_scopes" { ##finance_compute_service_account_scopes: This variable is a string type and its default value is "cloud-platform".
  type    = string
  default = "cloud-platform"
}
