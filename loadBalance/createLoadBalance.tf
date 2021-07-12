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
variable "NettyVPC_block" {
  default = "10.0.0.0/16"
}

variable "NettySubnet_1" {
  default = "10.0.1.0/24"
}

variable "NettySubnet_2" {
  default = "10.0.2.0/24"
}

# data

data "aws_availability_zones" "available" {}

data "aws_ami" "aws-linux" {
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
# PROVIDERS
##################################################################################

provider "aws" {
  access_key = var.aws_access_key
  secret_key = var.aws_secret_key
  region     = var.region
}

resource "aws_vpc" "NettyVPC" {
    cidr_block = var.NettyVPC_block
    enable_dns_hostnames = true

    tags ={
        Name = "NettyVPC"
    }
}

resource "aws_subnet" "NettySubnet_1" {
    vpc_id = aws_vpc.NettyVPC.id
    cidr_block = var.NettySubnet_1
    availability_zone = data.aws_availability_zones.available.names[0]
    map_public_ip_on_launch = true
    tags ={
        Name = "NettySubnet_1"
    }
}

resource "aws_subnet" "NettySubnet_2" {
    vpc_id = aws_vpc.NettyVPC.id
    cidr_block = var.NettySubnet_2
    availability_zone = data.aws_availability_zones.available.names[1]
    map_public_ip_on_launch = true
    tags ={
        Name = "NettySubnet_2"
    }
}

resource "aws_internet_gateway" "NettyIgw" {
    vpc_id = aws_vpc.NettyVPC.id
    tags ={
        Name = "NettyIgw"
    }
}

resource "aws_route_table" "publicRoute" {
    vpc_id = aws_vpc.NettyVPC.id
        route {
            cidr_block = "0.0.0.0/0"
            gateway_id = aws_internet_gateway.NettyIgw.id
        }
    tags ={
        Name = "publicRoute"
    }
}

resource "aws_route_table_association" "rt-NettySubnet_1" {
  subnet_id = aws_subnet.NettySubnet_1.id
  route_table_id = aws_route_table.publicRoute.id
}

resource "aws_route_table_association" "rt-NettySubnet_2" {
  subnet_id = aws_subnet.NettySubnet_2.id
  route_table_id = aws_route_table.publicRoute.id
}

resource "aws_security_group" "lb-sg" {
    name = "lb-sg"
    vpc_id = aws_vpc.NettyVPC.id

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

resource "aws_security_group" "allow_ssh_web" {
  name        = "allow_ssh_web"
  description = "Allow ssh and web access"
  vpc_id      = aws_vpc.NettyVPC.id

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
}

resource "aws_instance" "Server1" {
  ami                    = data.aws_ami.aws-linux.id
  instance_type          = "t2.micro"
  key_name               = var.key_name
  vpc_security_group_ids = [aws_security_group.allow_ssh_web.id]
  subnet_id = aws_subnet.NettySubnet_1.id
  connection {
    type        = "ssh"
    host        = self.public_ip
    user        = "ec2-user"
    private_key = file(var.private_key_path)

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
      Name = "Server1"
  }
}

resource "aws_instance" "Server2" {
  ami                    = data.aws_ami.aws-linux.id
  instance_type          = "t2.micro"
  key_name               = var.key_name
  vpc_security_group_ids = [aws_security_group.allow_ssh_web.id]
  subnet_id = aws_subnet.NettySubnet_2.id
  connection {
    type        = "ssh"
    host        = self.public_ip
    user        = "ec2-user"
    private_key = file(var.private_key_path)

  }

  provisioner "remote-exec" {
    inline = [
      "sudo yum install nginx -y",
      "sudo service nginx start",
      "sudo rm /usr/share/nginx/html/index.html",
      "echo '<html><head><title>Red Team Server</title></head><body style=\"background-color:#FE0000\"><p style=\"text-align: center;\"><span style=\"color:#FFFFFF;\"><span style=\"font-size:28px;\">Blue Team</span></span></p></body></html>' | sudo tee /usr/share/nginx/html/index.html"
    ]
  }
  tags ={
      Name = "Server2"
  }
}

resource "aws_lb" "test-lb-tf" {
  name               = "test-lb-tf"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.lb-sg.id]
  subnets            = [aws_subnet.NettySubnet_1.id, aws_subnet.NettySubnet_2.id]

  enable_deletion_protection = false

}

resource "aws_lb_listener" "web_listener" {
  load_balancer_arn = aws_lb.test-lb-tf.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.Netty_target_group.arn
  }
}

resource "aws_lb_target_group" "Netty_target_group" {
  name     = "Netty-target-group"
  port     = 80
  protocol = "HTTP"
  vpc_id   = aws_vpc.NettyVPC.id
}

resource "aws_lb_target_group_attachment" "attachServer1" {
  target_group_arn = aws_lb_target_group.Netty_target_group.arn
  target_id        = aws_instance.Server1.id
  port             = 80
}

resource "aws_lb_target_group_attachment" "attachServer2" {
  target_group_arn = aws_lb_target_group.Netty_target_group.arn
  target_id        = aws_instance.Server2.id
  port             = 80
}

output "aws_lb_public_dns" {
  value = aws_lb.test-lb-tf.dns_name
}