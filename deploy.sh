#!/bin/bash
{
# Deploys Django app on Ubuntu

# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install Git
sudo apt-get install git -y

# Configure Apache2
sudo apt-get install apache2 -y
sudo systemctl enable apache2
sudo apt-get install libapache2-mod-wsgi-py3
sudo a2enmod wsgi

# Clone Django app repo
cd /var/www/
sudo git clone https://github.com/InnerProduct97/parallel_ec2.git
sudo chown -R ubuntu:ubuntu parallel_ec2/
cd parallel_ec2/



# Install Python and Django dependencies
sudo apt-get install python3-pip python3-dev libpq-dev -y
sudo pip3 install virtualenv
virtualenv env
source env/bin/activate
pip3 install -r requirements.txt
./manage.py migrate
python manage.py crontab add
sudo service cron start

public_ip=$(curl http://checkip.amazonaws.com/)


# Create Apache2 Virtual Host
sudo touch /etc/apache2/sites-available/parallel_ec2.conf
sudo echo "
<VirtualHost *:80>
        ServerName $public_ip
        DocumentRoot /var/www/parallel_ec2

        ErrorLog /var/log/vhost.log

        Alias /static /var/www/parallel_ec2/static
        <Directory /var/www/parallel_ec2/static>
                Require all granted
        </Directory>

        Alias /media /var/www/parallel_ec2/media
        <Directory /var/www/parallel_ec2/media>
                Require all granted
         </Directory>

        <Directory /var/www/parallel_ec2/matan_assignment_ex2>
                <Files wsgi.py>
                        Require all granted
                </Files>
        </Directory>

        WSGIDaemonProcess matan_assignment_ex2 python-path=/var/www/parallel_ec2 python-home=/var/www/parallel_ec2/env
        WSGIProcessGroup matan_assignment_ex2
        WSGIScriptAlias / /var/www/parallel_ec2/matan_assignment_ex2/wsgi.py

</VirtualHost>
" | sudo tee /etc/apache2/sites-available/parallel_ec2.conf

# Enable Virtual Host
sudo a2ensite parallel_ec2.conf

# Changing Apache User and Group

# Replace the User line in apache2.conf
sudo sed -i "s/^User \${APACHE_RUN_USER}$/User ubuntu/" /etc/apache2/apache2.conf

# Replace the Group line in apache2.conf
sudo sed -i "s/^Group \${APACHE_RUN_GROUP}$/Group ubuntu/" /etc/apache2/apache2.conf

# Restart Apache2
sudo systemctl restart apache2
} &> deploy.log
echo "App is deployed successfully!"
echo "You can access it through the URL:http://$public_ip/"
