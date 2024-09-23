resource "aws_vpc" "AppVPC" {
    cidr_block = "10.0.0.0/16"
    enable_dns_support = true
    enable_dns_hostnames = true

    tags = {
        Name = "AppVPC"
    }
}

resource "aws_subnet" "AppSubnet1" {
    vpc_id = aws_vpc.AppVPC.id
    cidr_block = "10.0.1.0/24"
    availability_zone = "us-east-1a"

    tags = {
        Name = "AppSubnet1"
    }
}

resource "aws_subnet" "AppSubnet2" {
    vpc_id = aws_vpc.AppVPC.id
    cidr_block = "10.0.2.0/24"
    availability_zone = "us-east-1b"

    tags = {
        Name = "AppSubnet2"
    }
}

resource "aws_security_group" "WebTrafficSG" {
  vpc_id = aws_vpc.AppVPC.id
  name   = "WebTrafficSG"

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

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 3306
    to_port     = 3306
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "WebTrafficSG"
  }
}

resource "aws_network_interface" "nw-interface1" {
    security_groups = [aws_security_group.WebTrafficSG.id]
    subnet_id = aws_subnet.AppSubnet1.id

    tags = {
        Name = "nw-interface1"
    }
}
resource "aws_network_interface" "nw-interface2" {
    security_groups = [aws_security_group.WebTrafficSG.id]
    subnet_id = aws_subnet.AppSubnet2.id

    tags = {
        Name = "nw-interface2"
    }
}

resource "aws_internet_gateway" "AppInternetGateway" {
    vpc_id = aws_vpc.AppVPC.id

    tags = {
        Name = "AppInternetGateway"
    }
}

resource "aws_route_table" "AppRouteTable" {
    vpc_id = aws_vpc.AppVPC.id

    tags = {
        Name = "AppRouteTable"
    }
}

output "route_table_ID" {
    value = aws_route_table.AppRouteTable.id
}

resource "aws_eip" "public_ip1" {
    vpc = true
    network_interface = aws_network_interface.nw-interface1.id
}

resource "aws_eip" "public_ip2" {
    vpc = true
    network_interface = aws_network_interface.nw-interface2.id
}
