## The code defines several variables that are used to set the configuration of an artifact repository.
# The "variable" block defines the following variables:
variable "artifact_repository_iam_role_binding" {
  default = "roles/artifactregistry.writer" ## "artifact_repository_iam_role_binding": The default IAM role binding for the artifact repository, set to "roles/artifactregistry.writer".
  type    = string
}

variable "artifact_repository_iam_members" {
  default = "user:cloud@ineuron.ai"   ## "artifact_repository_iam_members": The default IAM member, set to "user:cloud@ineuron.ai".
  type    = string
}

variable "project_name" {
  default = "industry-ready-finance"  ## "project_name": The name of the project, set to "industry-ready-finance".
  type    = string
}

variable "artifact_repository_location" {  
  default = "us-central1"       ## "artifact_repository_location": The location of the artifact repository, set to "us-central1".
  type    = string
}

variable "artifact_repository_repository_id" {
  default = "finance-repository"    ## "artifact_repository_repository_id": The ID of the artifact repository, set to "finance-repository".
  type    = string
}

variable "artifact_repository_format" {
  default = "DOCKER"    ## "artifact_repository_format": The format of the artifact repository, set to "DOCKER".
  type    = string
}