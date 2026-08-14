terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

# IAM role for the EC2 instance
resource "aws_iam_role" "secure_role" {
  name = "secureiac-ec2-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Principal = {
          Service = "ec2.amazonaws.com"
        }

        Action = "sts:AssumeRole"
      }
    ]
  })
}

# Instance profile to attach the IAM role to EC2
resource "aws_iam_instance_profile" "secure_profile" {
  name = "secureiac-ec2-profile"
  role = aws_iam_role.secure_role.name
}

# Security group
resource "aws_security_group" "insecure_sg" {
  name        = "secureiac-security-group"
  description = "Security group for SecureIaC test instance"

  ingress {
    description = "Allow SSH from private network"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]
  }

  egress {
    description = "Allow outbound HTTPS traffic"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# EC2 instance
resource "aws_instance" "secure_instance" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"

  vpc_security_group_ids = [
    aws_security_group.insecure_sg.id
  ]

  # Checkov CKV_AWS_126
  monitoring = true

  # Checkov CKV_AWS_135
  ebs_optimized = true

  # Checkov CKV_AWS_79
  metadata_options {
    http_endpoint = "enabled"
    http_tokens   = "required"
  }

  # Checkov CKV_AWS_8
  root_block_device {
    encrypted = true
  }

  # Checkov CKV2_AWS_41
  iam_instance_profile = aws_iam_instance_profile.secure_profile.name
}