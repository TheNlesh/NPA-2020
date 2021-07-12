# ##################################################################################
# # VARIABLES
# ##################################################################################

# variable "aws_access_key" {}
# variable "aws_secret_key" {}
# variable "private_key_path" {}
# variable "key_name" {}
# variable "region" {
#   default = "us-east-1"
# }
# variable "network_address_space" {
#   default = "10.0.0.0/16"
# }
# variable "subnet1_address_space" {
#   default = "10.0.1.0/24"
# }

# ##################################################################################
# # PROVIDERS
# ##################################################################################

# provider "aws" {
#   access_key = var.aws_access_key
#   secret_key = var.aws_secret_key
#   region     = var.region
# }

# ##################################################################################
# # DATA
# ##################################################################################

# data "aws_ami" "aws-linux" {
#   most_recent = true
#   owners      = ["amazon"]

#   filter {
#     name   = "name"
#     values = ["amzn-ami-hvm*"]
#   }

#   filter {
#     name   = "root-device-type"
#     values = ["ebs"]
#   }

#   filter {
#     name   = "virtualization-type"
#     values = ["hvm"]
#   }
# }


# ##################################################################################
# # RESOURCES
# ##################################################################################

# resource "aws_vpc" "testVPC" {
#     cidr_block = var.network_address_space
#     enable_dns_hostnames = true

#     tags ={
#         Name = "testVPC"
#     }
# }

# resource "aws_subnet" "Public1" {
#     vpc_id = aws_vpc.testVPC.id
#     cidr_block = var.subnet1_address_space
#     map_public_ip_on_launch = true

#     tags ={
#         Name = "Public1"
#     }
# }

# resource "aws_internet_gateway" "testIgw" {
#     vpc_id = aws_vpc.testVPC.id

#     tags ={
#         Name = "testIgw"
#     }
# }

# resource "aws_route_table" "publicRoute" {
#     vpc_id = aws_vpc.testVPC.id
#         route {
#             cidr_block = "0.0.0.0/0"
#             gateway_id = aws_internet_gateway.testIgw.id
#         }
#     tags ={
#         Name = "publicRoute"
#     }
# }

# resource "aws_route_table_association" "rt-pubsub1" {
#   subnet_id = aws_subnet.Public1.id
#   route_table_id = aws_route_table.publicRoute.id
# }

# resource "aws_security_group" "allow_ssh_web" {
#   name        = "npaWk11_demo"
#   description = "Allow ssh and web access"
#   vpc_id      = aws_vpc.testVPC.id

#   ingress {
#     from_port   = 22
#     to_port     = 22
#     protocol    = "tcp"
#     cidr_blocks = ["0.0.0.0/0"]
#   }
#   ingress {
#     from_port   = 80
#     to_port     = 80
#     protocol    = "tcp"
#     cidr_blocks = ["0.0.0.0/0"]
#   }
#   egress {
#     from_port   = 0
#     to_port     = 0
#     protocol    = -1
#     cidr_blocks = ["0.0.0.0/0"]
#   }
# }

# resource "aws_instance" "Server1" {
#   ami                    = data.aws_ami.aws-linux.id
#   instance_type          = "t2.micro"
#   key_name               = var.key_name
#   vpc_security_group_ids = [aws_security_group.allow_ssh_web.id]
#   subnet_id = aws_subnet.Public1.id
  
#   connection {
#     type        = "ssh"
#     host        = self.public_ip
#     user        = "ec2-user"
#     private_key = file(var.private_key_path)

#   }

#   provisioner "remote-exec" {
#     inline = [
#       "sudo yum install nginx -y",
#       "sudo service nginx start",
#       "sudo rm /usr/share/nginx/html/index.html",
#       "echo '<html><head><title>Blue Team Server</title></head><body style=\"background-color:#1F778D\"><p style=\"text-align: center;\"><span style=\"color:#FFFFFF;\"><span style=\"font-size:28px;\">Blue Team</span></span></p></body></html>' | sudo tee /usr/share/nginx/html/index.html"
#     ]
#   }
#   tags ={
#       Name = "Server1"
#   }
# }

# ##################################################################################
# # OUTPUT
# ##################################################################################

# output "aws_instance_public_ip" {
#   value = aws_instance.Server1.public_ip
# }