#!/usr/bin/env bash

clear
echo "Installing virtualenv..."
virtualenv env
source env/bin/activate
pip install -r requirements.txt

echo "Installing Wordplease..."
python manage.py migrate

echo "Installing initial data..."
python manage.py loaddata users blogs

clear
echo "Your Django user:"
python manage.py createsuperuser

clear
echo "Running tests..."
python manage.py test
deactivate

echo "Creating media folder..."
mkdir media

clear
echo "There you go! Happy blogging!"
echo ""
echo "Run the following commands to see the magic:"
echo "$ source env/bin/activate  # activates the virtual enviroment"
echo "$ python manage.py runserver  # runs Django test server"
echo "In a different terminal:"
echo "$ source env/bin/activate  # activates the virtual enviroment"
echo "$ python manage.py celery worker  # runs celery worker"
