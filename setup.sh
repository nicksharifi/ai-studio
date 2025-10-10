#!/bin/bash

sudo apt update
sudo apt upgrade -y
sudo apt install build-essential  net-tools ffmpeg htop iftop python3-pip openssl -y
sudo apt install apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb https://download.docker.com/linux/ubuntu focal stable"
sudo apt install docker-ce -y
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-linux-`uname -m`" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose



SCRIPT_DIR="$(dirname "$(realpath "$0")")"
echo $SCRIPT_DIR
# Write the directory to the /etc/ai-studio/project_setting.conf file
# Create /etc/ai-studio if it doesn't exist
sudo mkdir -p /etc/ai-studio
echo "work_dir=$SCRIPT_DIR/tmp" | sudo tee /etc/ai-studio/setting.conf

sudo mkdir -p ./log
touch ./log/cerr.log

# Directory where the certificates will be stored
CERT_DIR="$SCRIPT_DIR/src/utils/secret_files/certs"

# Check if the directory exists, create if it doesn't
if [ ! -d "$CERT_DIR" ]; then
    mkdir -p "$CERT_DIR"
fi

# Set the certificate details
COMPANY_NAME="ai-studio"
EMAIL="ariyansharifi@gmail.com"

# Generate the certificate
openssl req -x509 -newkey rsa:4096 -nodes -keyout "$CERT_DIR/key.pem" -out "$CERT_DIR/cert.pem" -days 3650 \
    -subj "/C=US/ST=YourState/L=YourCity/O=$COMPANY_NAME/CN=$COMPANY_NAME/emailAddress=$EMAIL"

# Print completion message
echo "Certificate and key have been generated in $CERT_DIR"