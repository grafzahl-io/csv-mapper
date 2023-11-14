init:
	pip install virtualenv
	python -m venv env
	source env/bin/activate
install:
	pip install -r requirements.txt