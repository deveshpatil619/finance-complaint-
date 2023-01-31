## The above Terraform code creates two resources:
resource "random_integer" "random" {
  min = 1                ## random_integer: It is a Terraform resource of type random_integer and is named "random".
                          ## This resource generates a random integer between 1 and 50000 and stores it in the id attribute.
  max = 50000
}

resource "aws_s3_bucket" "model_bucket" {
  bucket        = "${random_integer.random.id}${var.model_bucket_name}"  ## aws_s3_bucket: It is a Terraform resource of type aws_s3_bucket and is named "model_bucket".
                                                                        ## This resource creates an S3 bucket in AWS with the name being a combination of the random integer 
                                                                        ## generated in the random_integer resource and the model_bucket_name variable.
                                                                        ## The force_destroy attribute is set to the value of the force_destroy_bucket variable.
  force_destroy = var.force_destroy_bucket
}
