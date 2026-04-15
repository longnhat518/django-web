python manage.py migrate
python manage.py runserver

python manage.py makemigrations
python manage.py migrate

python -X utf8 manage.py dumpdata --exclude auth.permission --exclude contenttypes -o db.json

Get-ChildItem db.json | Select-Object Length

python -X utf8 manage.py loaddata db.json
