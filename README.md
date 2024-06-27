# Flash Cards - Web application
* This is a web application for storing a collection of
online flash cards for studying using flask.

Note: This repo is the staging branch where all the commits would be made, and tested, before pushing to main branch

## How to Run Locally:
* `git clone https://gitlab.com/thi-wi/sweng/m-egm/team14.git`
* Dependencies - `pip install -r requirements.txt`
* To Run app -`flask run`
* To Run with debug mode - `flask run --debug`

## Run as Docker Service
* `git clone https://gitlab.com/thi-wi/sweng/m-egm/team14.git`
* Dependencies - `pip install -r requirements.txt`, [Docker App](https://www.docker.com/products/docker-desktop/)
* Create container -`docker build -t team14_web:latest .`
  * Or build container and run immediately - `docker-compose up --build`
* Pull contained from docker hub and Run - `docker run -d -p 8080:5000 team14_web:latest`
  * after running check [FLASH CARD APP](http://127.0.0.1:5000/)
* List all running containers - `docker ps`
* Stop running container - `docker stop <container id>`

## Testing
* Run - `python -m pytest`
* Load-test - `locust -f ./load_testing.py`

## Git Commits
* Run - `flake8 .` before pushing in order to keep our coding standards, have shared the .flake8 for exclusions
