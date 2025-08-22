## Migrations (make migrations)
migrations:
	docker compose exec web python manage.py makemigrations
	docker compose exec web python manage.py migrate


## Server
up:
	docker compose up --build

down:
	docker compose down -v

## Fixture
seed:
	docker compose exec web python manage.py loaddata qa/fixtures/seed.json

seed-demo:
	docker compose exec web python manage.py seed_demo

## Manage