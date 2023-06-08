#!/bin/bash

sudo apt-get install python3-pip
pip3 install requests


# Change to the appropriate directory
cd /home/ubuntu/

# Create a cron job entry
cron_entry="*/2 * * * * cd /home/ubuntu && python3 main.py >> /home/ubuntu/logfile.log 2>&1"

# Add the cron job entry to the crontab
(crontab -l 2>/dev/null; echo "$cron_entry") | crontab -

echo "Cron job set to run Python Script every minute."
