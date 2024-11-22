# Population Health Platform #
This repo contains the code for Population Health Platform

## Branches
* There are majorly three branches `develop`, `uat` and `production` public facing
* Production branch points to live environment, uat to testing environment, develop to development environment
* Feature branches will be used by developers to work on a new feature or bug fixes by taking a fresh branch from `develop`

### Workflow
* Developers should create a feature branch from `develop` branch
* Once the work is complete, create a PR with `develop`
* To make the new feature live, PR of uat is  needed to merge in production
* Mention Jira ticket number in PR title, and commit message.

## Contributing

#### Technology Stack
* Python 3.10.2 - [Official Download Link](https://www.python.org/downloads/)
* Django 4.0 - [Official Link](https://www.djangoproject.com/)
* MySQL - [Official Download Link](https://www.mysql.com/downloads/)


#### Development Setup
##### Git & Clone Code
Write this command in the directory where you want to place the project 

```bash
git clone https://badarIqbal@bitbucket.org/wsaddo/pop-health-backend.git
```

##### Virtual Environment
Create and activate virtual environment and then install the requirements. 
```bash
cd backend
python -m venv .venv                      # First time

#windows
. ./.venv/Scripts/activate                # In every new terminal window
pip install -r requirements/local.txt     # First time, and if new package is added
```

##### Database 
```bash
# MacOS based settings
# mysql  -> write into your terminal to write commands ->Login into DB user
# List of existing database
CREATE DATABASE pop_health_dev; # Confirm new database 
# The user according .envs/.sample.env
CREATE USER 'root' WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE 'pop_health_dev' TO username;
```

##### Database Migrations
For development environment setup,

```bash
python manage.py makemigrations
python manage.py migrate
```

##### Run Application
```bash
python manage.py runserver
```

Access Website at: [localhost:8000](localhost:8000)

## Deployment
