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
variable "network_address_space" {
  default = "10.0.0.0/16"
}
variable "subnet1_address_space" {
  default = "10.0.1.0/24"
}



##################################################################################
# PROVIDERS
##################################################################################

provider "aws" {
  access_key = var.aws_access_key
  secret_key = var.aws_secret_key
  region     = var.region
}

##################################################################################
# DATA
##################################################################################

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
# RESOURCES
##################################################################################


# NETWORKING #
resource "aws_vpc" "vpc" {
  cidr_block = var.network_address_space
  enable_dns_hostnames = true

  tags ={
      Name = "ansibleLab"
  }
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.vpc.id

  tags ={
      Name = "igw"
  }

}

resource "aws_subnet" "subnet1" {
  cidr_block              = var.subnet1_address_space
  vpc_id                  = aws_vpc.vpc.id
  map_public_ip_on_launch = "true"
  availability_zone       = data.aws_availability_zones.available.names[0]

  tags ={
      Name = "subnet1"
  }

}



# ROUTING #
resource "aws_route_table" "rtb" {
  vpc_id = aws_vpc.vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags ={
      Name = "Internet Route"
  }

}

resource "aws_route_table_association" "rta-subnet1" {
  subnet_id      = aws_subnet.subnet1.id
  route_table_id = aws_route_table.rtb.id
}

# SECURITY GROUPS #
# ssh security group 
resource "aws_security_group" "ssh-sg" {
  name   = "ssh_sg"
  vpc_id = aws_vpc.vpc.id

  # SSH access from anywhere
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

  tags ={
      Name = "sshrule"
  }
}


# INSTANCES #
resource "aws_instance" "ansible" {
  ami                    = data.aws_ami.aws-linux-2.id
  instance_type          = "t2.micro"
  subnet_id              = aws_subnet.subnet1.id
  vpc_security_group_ids = [aws_security_group.ssh-sg.id]
  key_name               = var.key_name

  connection {
    type        = "ssh"
    host        = self.public_ip
    user        = "ec2-user"
    private_key = file(var.private_key_path)

  }


  provisioner "remote-exec" {
    inline = [
        "sudo yum update -y",
        "sudo amazon-linux-extras install ansible2 -y",
        "ls -a",
        "ls -a"

    ]
  }

  tags ={
      Name = "ansibleNode"
  }

}

resource "aws_instance" "web" {
  ami                    = data.aws_ami.aws-linux-2.id
  instance_type          = "t2.micro"
  subnet_id              = aws_subnet.subnet1.id
  vpc_security_group_ids = [aws_security_group.ssh-sg.id]
  key_name               = var.key_name

  connection {
    type        = "ssh"
    host        = self.public_ip
    user        = "ec2-user"
    private_key = file(var.private_key_path)

  }

  provisioner "remote-exec" {
    inline = [
        "sudo yum update -y",
        "ls -a"

    ]
  }

  tags ={
      Name = "web"
  }

}
resource "aws_instance" "db1" {
  ami                    = data.aws_ami.aws-linux-2.id
  instance_type          = "t2.micro"
  subnet_id              = aws_subnet.subnet1.id
  vpc_security_group_ids = [aws_security_group.ssh-sg.id]
  key_name               = var.key_name

    connection {
        type        = "ssh"
        host        = self.public_ip
        user        = "ec2-user"
        private_key = file(var.private_key_path)

    }


  provisioner "remote-exec" {
    inline = [
        "sudo yum update -y",
        "ls -a"

    ]
  }

  tags ={
      Name = "db1"
  }
}

  ##################################################################################
  # OUTPUT
  ##################################################################################

output "aws_instance_private_ip_web" {
value = aws_instance.web.private_ip
}

output "aws_instance_public_ip_web" {
value = "ssh -i vockey.pem ec2-user@${aws_instance.web.public_ip}"
}

output "aws_instance_private_ip_db1" {
value = aws_instance.db1.private_ip
}
output "aws_instance_public_ip_db1" {
value = "ssh -i vockey.pem ec2-user@${aws_instance.db1.public_ip}"
}

output "aws_instance_public_ip_ansibleNode" {
value = "ssh -i vockey.pem ec2-user@${aws_instance.ansible.public_ip}"
}