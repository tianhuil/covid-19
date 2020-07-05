SHELL := /bin/bash

# set variables
export NAME = covid-19

create-install:
	python3 -m venv venv
	source venv/bin/activate \
		&& pip3 install -r requirements.txt \
		&& ipython kernel install --user --name=$$NAME

install:
	source venv/bin/activate && pip3 install -r requirements.txt

ipython:
	source venv/bin/activate && ipython --pdb

jupyter:
	source venv/bin/activate && jupyter notebook

flask:
	source venv/bin/activate && FLASK_ENV=development FLASK_APP=app flask run

voila:
	source venv/bin/activate && python -m voila NYTimes_Data_Analysis.ipynb
