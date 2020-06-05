# Enogrid - ACdC

# Virtual environment
pipenv install --dev
pipenv shell

# API local
flask run

# Automate
celery -A app.celery worker

# Pytest
pytest --ignore=data