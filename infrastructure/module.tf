## The code is written in Terraform and is used to define the infrastructure for a financial application. 
## The code has three main components:

terraform {
  backend "s3" {  ## The backend provides a central location to store the Terraform state, which helps maintain consistency and prevent conflicts. 
    bucket = "finance-tf-state"
    key    = "tf_state"
    region = "ap-south-1"
  }
}

# These modules represent different components of the infrastructure and are defined in separate Terraform
# files in the "./finance_artifact_repository", "./finance_model_bucket", and "./finance_virtual_machine" directories, respectively 

module "finance_artifact_repository" {
  source = "./finance_artifact_repository"
}

module "finance_model_bucket" {
  source = "./finance_model_bucket"
}

module "finance_virtual_machine" {
  source = "./finance_virtual_machine"
}







