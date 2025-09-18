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
seed-all:
	docker compose exec web python manage.py loaddata qa/fixtures/seed.json
	docker compose exec web python manage.py seed_demo
	docker compose exec web python manage.py seed_exam --if-empty

seed-exam:
	docker compose exec web python manage.py seed_exam --if-empty

## Manage
super:
	docker compose exec web python manage.py createsuperuser

