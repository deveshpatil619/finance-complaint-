##"This block defines a data source for reading a Google Cloud IAM policy and creates a "google_iam_policy" resource named "admin".
data "google_iam_policy" "admin" {
  binding {  ## "binding": This block defines the details of the IAM policy binding. It specifies the role, which is taken from the variable "finance_iam_user_role", 
    role = var.finance_iam_user_role 
    members = [
      var.finance_iam_user_email, ## and the members who are authorized to assume the role, in this case, a single member "finance_iam_user_email".
    ]
  }
}
##  This block creates a resource for setting an IAM policy for a Google Compute Instance.
resource "google_compute_instance_iam_policy" "finance_compute_instance_iam_policy" {
  project       = google_compute_instance.finance_compute_instance.project ## "project": The Google Cloud project for which the policy is set.
  zone          = google_compute_instance.finance_compute_instance.zone ## "zone": The zone in which the compute instance is located.
  instance_name = google_compute_instance.finance_compute_instance.name ## "instance_name": The name of the compute instance for which the IAM policy is being set.
  policy_data   = data.google_iam_policy.admin.policy_data ## "policy_data": The IAM policy data that is read from the data source "google_iam_policy.admin".
}



