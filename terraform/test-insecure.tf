provider "aws" {
  region = "ap-south-1"
}

resource "aws_s3_bucket" "app_data" {
  bucket = "app-data-prod-8841"
}

resource "aws_s3_bucket_public_access_block" "app_data" {
  bucket            = aws_s3_bucket.app_data.id
  block_public_acls = false
}

resource "aws_security_group" "web_sg" {
  name = "web-sg"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
