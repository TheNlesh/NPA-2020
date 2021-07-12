##################################################################################
# VARIABLES
##################################################################################

variable "aws_access_key" {}
variable "aws_secret_key" {}
variable "private_key_path" {}
variable "key_name" {}
variable "region" {
  default = "us-east-1"
}
variable "NPA_VPC" {
  default = "10.1.0.0/16"
}

variable "PublicSubnet1" {
  default = "10.1.0.0/24"
}

variable "PublicSubnet2" {
  default = "10.1.1.0/24"
}

# data

data "aws_availability_zones" "available" {}

data "aws_ami" "aws-linux-2" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm*"]
  }

  filter {
    name   = "root-device-type"
    values = ["ebs"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

##################################################################################
# PROVIDERS
##################################################################################

provider "aws" {
  access_key = var.aws_access_key
  secret_key = var.aws_secret_key
  region     = var.region
}

resource "aws_vpc" "NPA_VPC" {
    cidr_block = var.NPA_VPC
    enable_dns_hostnames = true
    tags = {
        name = "NPA21-60070062-VPC"
    }
}

resource "aws_subnet" "PublicSubnet1" {
    vpc_id = aws_vpc.NPA_VPC.id
    cidr_block = var.PublicSubnet1
    availability_zone = "us-east-1a"
    map_public_ip_on_launch = true
    tags = {
        name = "Public-60070062-1"
    }
}

resource "aws_subnet" "PublicSubnet2" {
    vpc_id = aws_vpc.NPA_VPC.id
    cidr_block = var.PublicSubnet2
    availability_zone = "us-east-1b"
    map_public_ip_on_launch = true
    tags = {
        name = "Public-60070062-2"
    }
}

resource "aws_internet_gateway" "InternetGW" {
    vpc_id = aws_vpc.NPA_VPC.id
    tags = {
        Name = "NPA21-60070062-InternetGW"
    }
}

resource "aws_route_table" "publicRoute" {
    vpc_id = aws_vpc.NPA_VPC.id
        route {
            cidr_block = "0.0.0.0/0"
            gateway_id = aws_internet_gateway.InternetGW.id
        }
    tags ={
        Name = "NPA21-60070062-publicRouteTable"
    }
}

resource "aws_route_table_association" "rt-PublicSubnet1" {
  subnet_id = aws_subnet.PublicSubnet1.id
  route_table_id = aws_route_table.publicRoute.id
}

resource "aws_route_table_association" "rt-PublicSubnet2" {
  subnet_id = aws_subnet.PublicSubnet2.id
  route_table_id = aws_route_table.publicRoute.id
}

resource "aws_security_group" "allow_ssh_only" {
  name        = "allow_ssh_only"
  description = "Allow ssh access"
  vpc_id      = aws_vpc.NPA_VPC.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = -1
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = {
        Name = "NPA21-60070062-sg-0"
    }
}

resource "aws_security_group" "allow_ssh_web" {
  name        = "allow_ssh_web"
  description = "Allow ssh and web access"
  vpc_id      = aws_vpc.NPA_VPC.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = -1
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = {
        Name = "NPA21-60070062-sg-1"
    }
}

resource "aws_instance" "ansibleNode" {
  ami                    = data.aws_ami.aws-linux-2.id
  instance_type          = "t2.micro"
  key_name               = var.key_name
  vpc_security_group_ids = [aws_security_group.allow_ssh_only.id]
  subnet_id = aws_subnet.PublicSubnet1.id
  connection {
    type        = "ssh"
    host        = self.public_ip
    user        = "ec2-user"
    private_key = file(var.private_key_path)

  }

  tags ={
      Name = "NPA21-60070062-instance0"
  }
}



resource "aws_instance" "webNode" {
  ami                    = data.aws_ami.aws-linux-2.id
  instance_type          = "t2.micro"
  key_name               = var.key_name
  vpc_security_group_ids = [aws_security_group.allow_ssh_web.id]
  subnet_id = aws_subnet.PublicSubnet2.id
  connection {
    type        = "ssh"
    host        = self.public_ip
    user        = "ec2-user"
    private_key = file(var.private_key_path)

  }

  tags ={
      Name = "NPA21-60070062-instance1"
  }
}

output "aws_instance0_public_dns" {
  value = aws_instance.ansibleNode.public_dns
}

output "aws_instance1_public_dns" {
  value = aws_instance.webNode.public_dns
}