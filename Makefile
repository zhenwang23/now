# Usages:
#
# to install all dependencies:
# $ make init
#
# to run style check:
# $ make style

init:
	pip install -r requirements.txt
style:
	black -S .
	flake8 ./src
	isort .
	pycln .
