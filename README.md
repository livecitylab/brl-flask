# Data Analysis for berlinrents.live

This repository contains a [Flask](https://scrapy.org/) server providing endpoints to the frontend app for data analysis and predicitions.

## How does it work?

For each request, the server gets data from our GraphQL endpoint (https://brl-hasura.herokuapp.com/v1/graphql) and feeds it into the required functions. Some endpoints return JSON responses, while other return a [Plotly Dash](https://plotly.com/dash/) app, which is then embedded in the frontend inside a `<iframe>` tag.

## Installation

To install this package, you'll have to fork it and install its dependencies with:

`pip install -r requirements.txt`

## Usage

You can run the Flask app locally by using the command:

`python wsgi.py`

## Deployment

The server is hosted on a Heroku dyno. Files necessary for Heroku are:

- `Procfile`: to define the command to run _scrapyd_ after deployment
- `runtime.txt`: to define the Python version Heroku should use

Current app on Heroku (on techlabsprojectteam@gmail.com account):

- Dashboard [https://dashboard.heroku.com/apps/brl-flask](https://dashboard.heroku.com/apps/brl-flask)
- URL [https://brl-flask.herokuapp.com/](https://brl-flask.herokuapp.com/)

To deploy a new version, commit your changes and push to `master` on Github. The app is setup to deploy from there, automatically.
