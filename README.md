# Enogrid - ACdC

# Virtual environment
pipenv install --dev<br/>
pipenv shell

# API local
flask run

# Automate
celery -A app.celery worker

# Pytest
pytest --ignore=data