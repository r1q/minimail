init:
	./manage.py makemigrations user_management
	./manage.py makemigrations subscriber_management
	./manage.py makemigrations template_management
	./manage.py makemigrations campaign_management
	./manage.py makemigrations analytics_management
	./manage.py migrate
	./manage.py createsuperuser

clean:
	rm -rf user_management/migrations
	rm -rf subscriber_management/migrations
	rm -rf campaign_management/migrations
	rm -rf template_management/migrations
	rm -rf analytics_management/migrations

	rm -rf user_management/__pycache__
	rm -rf subscriber_management/__pycache__
	rm -rf campaign_management/__pycache__
	rm -rf template_management/__pycache__
	rm -rf analytics_management/__pycache__
