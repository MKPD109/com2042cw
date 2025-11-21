# COM2042 Lab Assignments Repo

## Getting started
- Navigate to the repo folder after cloning it
- Create a virtual environment `python3 -m venv venv`
- Install the dependencies into the venv by running `python3 -m pip install -r requirements.txt`

The following commands will be run against all submissions:
- `python3 manage.py compilemessages`, to generate localised strings;
- `python3 manage.py makemigrations`, to generate migrations, in case they were not supplied;
- `python3 manage.py migrate`, to perform the migrations to the local database;
- `python3 manage.py bootstrap`, to insert any starting data into the database (e.g. groups, permissions);
- `python3 manage.py test`, to run your tests; and,
- `python3 manage.py runserver`, to run your Django web application.

## Important
You should not change anything inside the MusicDBInc folder, nor `requirements.txt`. If you think something is missing, please let us know first.

## Submitting
You must commit your work to the `main` branch in your individual Surrey GitLab repository for this module. The last commit on this branch will be marked.
