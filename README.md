# Enogrid - ACdC

## Requirements
- `python3` + `pipenv`
- [`docker`](https://docs.docker.com/install/linux/docker-ce/ubuntu/)
- [`docker-compose`](https://docs.docker.com/compose/install/)

## Launch pipenv
- pipenv install --three<br/>
- pipenv shell

## PostgreSQL

Using `docker-compose`, you can manage a local PostgreSQL:

1. Run: `sudo docker-compose up -d`
2. Check: `sudo docker-compose ps`
3. Watch the logs: `sudo docker-compose logs`
4. Run the database shell:

```
    sudo docker exec -it enogrid-acdc_postgres_1 psql -h postgres -U enogrid enogrid_acdc
    Password for user enogrid: password

    santa_data=# \dt; (See tables)
    santa_data=# SELECT * FROM table;
    santa_data=# \q ((quit)
```

5. Stop: `sudo docker-compose down`
6. Remove data: `rm -rf ./data`


## API local
flask run

## Automate
celery -A app.celery worker

## Pytest
pytest --ignore=data