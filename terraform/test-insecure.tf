provider "aws" {
  region     = "us-east-1"
  access_key = "AKIAIOSFODNN7EXAMPLE" # Hardcoded secret
  secret_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY" # Hardcoded secret
}

resource "aws_s3_bucket" "insecure_bucket" {
  bucket = "my-company-leaked-data-bucket"
  # Missing public access block and default encryption
}

resource "aws_security_group" "allow_all" {
  name        = "allow_all"
  description = "Open to the world"

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"] # Overly permissive wildcard access
  }
}
