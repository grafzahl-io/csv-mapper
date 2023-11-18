init:
	source env/bin/activate

stop:
	 ~ deactivate

install:
	pip install virtualenv
	python -m venv env
	source env/bin/activate
	pip install -r requirements.txt