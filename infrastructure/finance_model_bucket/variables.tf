## The code defines Terraform variables for AWS.
##The following variables are defined:

variable "aws_region" {
  type    = string        ## aws_region: The AWS region where the resources will be deployed. The default value is "ap-south-1".
  default = "ap-south-1"
}

variable "model_bucket_name" {
  type    = string      ## model_bucket_name: The name of the model bucket to store the finance data. The default value is "finance-cat-service".
  default = "finance-cat-service"
}

variable "aws_account_id" {
  type    = string    ## aws_account_id: The AWS account ID where the resources will be deployed. The default value is "566373416292".
  default = "566373416292"
}

variable "force_destroy_bucket" {
  type    = bool    ## force_destroy_bucket: A boolean value to specify whether the bucket should be destroyed even if it is not empty. The default value is "true".
  default = true
}

variable "iam_policy_principal_type" {
  type    = string    ## iam_policy_principal_type: The type of IAM policy principal. The default value is "AWS".
  default = "AWS"
}