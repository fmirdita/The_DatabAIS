# The DatabAIS
This Django app is the primary interface for both tracking and analyzing data for the Academic Innovation Studio. It's functionalities are:
  1) Provide an end-user interface for tracking service utilization and event attendance
  2) Provide AIS receptionists an interface to monitor and contribute to this data, and
  3) Allow easy access to key analytics 

## Sign-In Interface
The goal of this interface are to optimize the user experience while collecting desired data. Once registered in the system, they just scan their Cal ID or type in their email to sign in. If they are not signing in for an event, they are asked the reason for their visit.

## Reception Interface 
The goal of this interface is to allow mediation of the collected data. Receptionist are able to add comments to sign-ins, view who came in and why, set up event sign ins, etc. 

## Reporting
Reports are designed to provide key data analysis. They are simply a start date and end date, and a collection of queries on collected data. 

# Dev Environment Set Up
**Note:**
- As of 8/16/18, this code base lives in a private enterprise ETS github repository and requires permission to access. 
- These instructions are specific to Mac OS X with Python 3 and pip installed. 

### Get the databAIS source 
```
git clone https://github.berkeley.edu/ETS/ais-login-db.git
```

## Dependencies
### PipEnv
PipEnv is a virtual environment packaging tool (bundler, composer, npm, cargo, yarn, etc.). The use of pipenv allows for similar installation on Windows machines.
```
// Update Homebrew
$ brew update

// Install pipenv
$ brew install pipenv
```
### Instasll PostgreSQL
The databAIS uses [PostgreSQL](http://www.postgresql.org). Set up the required database and users:
```
// Install postgres
$ brew install postgresql

// Start postgres
$ postgres -D /usr/local/var/postgres

// Create a database and user
$createuser databais --no-createdb --no-superuser --no-createrole --pwprompt

// Enter (and re-enter) the password: databais

$createdb databais --owner=databias
```
### Install Django and all other dependencies
```
// Install Django
$ pipenv install django==2.0.7

// Install Import-Export package
$ pipenv install django-import-export

// Install PosgresSQL-Django dependency
$ pipenv install psycopg2-binary

// Activate virtual environment
$ pipenv shell
```

## Configure Django
### The databAIS database
In order to get Django to use the PosgreSQL database you've just set up, you'll need to go into `databais/settings.py` and update the `DATABASE` configuration variable.
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'databais',
        'USER': 'dtabais',
        'PASSWORD': 'databais',
        'HOST': 'localhost',
        'PORT': '',
    }
}
```
Then, you'll need to run initial migrations and create a super user so that you can access the admin interface. If you have python 2.7 and python 3 installed, you might need to run these commands using `python3` instead of `python`. 
`manage.py` is the file used to manage applications. These commands are run anytime changes are made to the schema in `models.py`.
```
// Make database migrations 
$ python manage.py makemigrations

// Run migrations to the database
$ python manage.py migrate
```
### The databAIS Admin
```
// Create superuser
$ python manage.py createsuperuser
// enter username, password, re-enter password

// Run local server
$ python manage.py runserver

// Open a browser and visit http://127.0.0.1:8000/admin
// Login to the Admin interface your set credentials
```
## Run tests
```
python manage.py test
```
