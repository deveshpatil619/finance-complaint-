## This Terraform code creates an Amazon S3 bucket policy that allows full access to the S3 bucket defined in 
## the "aws_s3_bucket" resource block. 

resource "aws_s3_bucket_policy" "allow_full_access" {
  bucket = aws_s3_bucket.model_bucket.id    
  policy = data.aws_iam_policy_document.allow_full_access.json   ##The policy is defined using an AWS IAM policy document data source (data "aws_iam_policy_document" "allow_full_access").
}

data "aws_iam_policy_document" "allow_full_access" {
  statement {  ##The principal(s) that the policy will apply to, defined using the type and identifiers variables, 
    principals {  ##which represent the principal type (in this case, AWS) and the AWS account ID respectively.
      type        = var.iam_policy_principal_type
      identifiers = [var.aws_account_id]
    }

    actions = ["s3:*"]  ##The actions the principal can perform, which in this case is defined as all actions available in S3 ("s3:*").

    resources = [
      aws_s3_bucket.model_bucket.arn, ##The resources the principal can access, which is defined as the ARN of 
      "${aws_s3_bucket.model_bucket.arn}/*", ##the S3 bucket created in the "aws_s3_bucket" resource block, as well as all its contents.
    ]
  }
}
