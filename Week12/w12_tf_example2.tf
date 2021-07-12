##################################################################################
# VARIABLES
##################################################################################

variable "aws_access_key_server2" {}
variable "aws_secret_key_server2" {}
variable "private_key_path_server2" {}
variable "key_name_server2" {}
variable "region_server2" {
  default = "us-east-1"
}
variable "network_address_space_server2" {
  default = "10.0.0.0/16"
}
variable "subnet1_address_space_server2" {
  default = "10.0.1.0/24"
}
variable "subnet2_address_space_server2" {
    default = "10.0.2.0/24"
}

##################################################################################
# PROVIDERS
##################################################################################

provider "aws" {
  access_key = var.aws_access_key_server2
  secret_key = var.aws_secret_key_server2
  region     = var.region_server2
  # alias  = "Server2"
}

##################################################################################
# DATA
##################################################################################
data "aws_availability_zones" "available" {}

data "aws_ami" "aws-linux_server2" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn-ami-hvm*"]
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
# RESOURCES
##################################################################################

resource "aws_vpc" "testVPC_server2" {
    cidr_block = var.network_address_space_server2
    enable_dns_hostnames = true

    tags ={
        Name = "testVPC"
    }
}

resource "aws_subnet" "Public1_server2" {
    vpc_id = aws_vpc.testVPC_server2.id
    cidr_block = var.subnet1_address_space_server2
    availability_zone = data.aws_availability_zones.available.names[0]
    map_public_ip_on_launch = true
    tags ={
        Name = "Public1"
    }
}

resource "aws_subnet" "Public2_server2" {
    vpc_id = aws_vpc.testVPC_server2.id
    cidr_block = var.subnet2_address_space_server2
    map_public_ip_on_launch = true
    availability_zone = data.aws_availability_zones.available.names[1]

    tags ={
        Name = "Public2"
    }
}

resource "aws_internet_gateway" "testIgw_server2" {
    vpc_id = aws_vpc.testVPC_server2.id

    tags ={
        Name = "testIgw"
    }
}

resource "aws_route_table" "publicRoute_server2" {
    vpc_id = aws_vpc.testVPC_server2.id
        route {
            cidr_block = "0.0.0.0/0"
            gateway_id = aws_internet_gateway.testIgw_server2.id
        }
    tags ={
        Name = "publicRoute"
    }
}

resource "aws_route_table_association" "rt-pubsub1_server2" {
  subnet_id = aws_subnet.Public1_server2.id
  route_table_id = aws_route_table.publicRoute_server2.id
}

resource "aws_route_table_association" "rt-pubsub2_server2" {
  subnet_id = aws_subnet.Public2_server2.id
  route_table_id = aws_route_table.publicRoute_server2.id
}

resource "aws_security_group" "elb-sg" {
    name = "elb-sg"
    vpc_id = aws_vpc.testVPC_server2.id

    ingress {
        from_port = 80
        to_port = 80
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]

    }

    egress {
        from_port = 0
        to_port = 0
        protocol = "-1"
        cidr_blocks = ["0.0.0.0/0"]
    }
}

resource "aws_security_group" "allow_ssh_web_server2" {
  name        = "npaWk12_demo_server2"
  description = "Allow ssh and web access"
  vpc_id      = aws_vpc.testVPC_server2.id

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
    cidr_blocks = [var.network_address_space_server2]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = -1
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_lb" "webLB" {
  name               = "webLB"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.allow_ssh_web_server2.id]
  subnets            = [aws_subnet.Public1_server2.id, aws_subnet.Public2_server2.id]

  enable_deletion_protection = true

  tags = {
    Environment = "production"
  }
}

resource "aws_instance" "Server2_with_LB" {
  ami                    = data.aws_ami.aws-linux_server2.id
  instance_type          = "t2.micro"
  key_name               = var.key_name_server2
  vpc_security_group_ids = [aws_security_group.allow_ssh_web_server2.id]
  subnet_id = aws_subnet.Public1_server2.id
  connection {
    type        = "ssh"
    host        = self.public_ip
    user        = "ec2-user"
    private_key = file(var.private_key_path_server2)

  }

  provisioner "remote-exec" {
    inline = [
      "sudo yum install nginx -y",
      "sudo service nginx start",
      "sudo rm /usr/share/nginx/html/index.html",
      "echo '<html><head><title>Blue Team Server</title></head><body style=\"background-color:#1F778D\"><p style=\"text-align: center;\"><span style=\"color:#FFFFFF;\"><span style=\"font-size:28px;\">Blue Team</span></span></p></body></html>' | sudo tee /usr/share/nginx/html/index.html"
    ]
  }
  tags ={
      Name = "Server2_with_LB"
  }
}


##################################################################################
# OUTPUT
##################################################################################

output "aws_lb_public_dns" {
  value = aws_lb.webLB.dns_name
}