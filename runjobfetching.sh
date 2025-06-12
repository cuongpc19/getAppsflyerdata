#!/bin/bash
cd /home/team_data/getAppsflyerdata
source venv/bin/activate
python manage.py fetch_data
