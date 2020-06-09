# Enogrid - ACdC

## Virtual environment
pipenv install --three<br/>
pipenv shell

## Docker compose
sudo docker-compose up -d<br/>
sudo docker-compose ps<br/>
sudo docker-compose logs<br/>
sudo docker exec -it enogrid-acdc_postgres_1 psql -h postgres -U [User](enogrid) [Data Base](enogrid_acdc)<br/>
sudo docker-compose down

## API local
flask run

## Automate
celery -A app.celery worker

## Pytest
pytest --ignore=data