# Enogrid - ACdC

## Virtual environment
pipenv install --three<br/>
pipenv shell

## API local
flask run

## Automate
celery -A app.celery worker

## Pytest
pytest --ignore=data