resource "aws_instance" "frontend" {
  ami             = "ami-06c68f701d8090592"
  instance_type   = "t2.large"

  network_interface {
    network_interface_id = aws_network_interface.nw-interface1.id
    device_index = 0
  }

  user_data = <<-EOF
              #!/bin/bash
              sudo yum update -y
              sudo yum install -y nginx
              sudo systemctl start nginx
              sudo systemctl enable nginx
              EOF

  key_name = "my-ec2-key"

  tags = {
    Name = "attendance-system-frontend"
  }
}

resource "aws_instance" "backend" {
  ami             = "ami-06c68f701d8090592"
  instance_type   = "t2.2xlarge"

  network_interface {
    network_interface_id = aws_network_interface.nw-interface2.id
    device_index = 0
  }

  key_name = "my-ec2-key"

  tags = {
    Name = "attendance-system-backend"
  }
}

output "instance1_id" {
  value = aws_instance.frontend.id
}

output "instance2_id" {
  value = aws_instance.backend.id
}