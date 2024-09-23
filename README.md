# Facial Attendance Web App

## Prerequisites
- Python 3.8
- Nginx
- Node.js and npm

## Setup Instructions

### Update and Install Dependencies

sudo apt-get update
sudo apt install -y python3-pip nginx

Configure Nginx
Create and edit the Nginx configuration file:

sudo nano /etc/nginx/sites-enabled/fastapi_nginx

Add the following configuration (replace <YOUR_EC2_IP> with your EC2 instance’s public IP):

server {
    listen 80;   
    server_name <YOUR_EC2_IP>;    
    location / {        
        proxy_pass http://127.0.0.1:8000;    
    }
}

Restart Nginx:

sudo service nginx restart

Update EC2 security-group settings for your instance to allow HTTP traffic to port 80.

Clone Repository
git clone https://github.com/Ammb305/facial-attendace-web-app.git
cd face-attendance-web-app-react-python

Backend Setup
Install Python 3.8 and create a virtual environment:

sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install python3.8 python3.8-dev python3.8-distutils python3-virtualenv
cd backend
virtualenv venv --python=python3.8
source venv/bin/activate
pip install cmake==3.25.0
pip install -r requirements.txt

Launch Backend
python3 -m uvicorn main:app

Frontend Setup
You can host the frontend locally (localhost) or on a server.

Setup Server
Launch a t2.large instance from AWS and SSH into the instance. Run the same commands as in the backend section to install Nginx.

The app will be launched on port 3000, so adjust the Nginx config file:

sudo nano /etc/nginx/sites-enabled/fastapi_nginx

Replace the configuration with:

server {
    listen 80;   
    server_name <YOUR_EC2_IP>;    
    location / {        
        proxy_pass http://127.0.0.1:3000;    
    }
}

Restart Nginx:

sudo service nginx restart

Update EC2 security-group settings for your instance to allow HTTP traffic to port 80.

Launch Frontend
git clone https://github.com/Ammb305/facial-attendace-web-app.git
cd facial-attendance-web-app/frontend/face-attendance-web-app-front/
sudo apt-get install npm
npm install
npm start

Edit the value of API_BASE_URL in src/API.js with the IP of the backend server.

Automated Infrastructure: Provisioned EC2 instances and configured security groups using Terraform

![terraform-aws-diagram](https://github.com/user-attachments/assets/0ca1fc35-c1ae-4455-ae03-d60a1c38e1ba)
