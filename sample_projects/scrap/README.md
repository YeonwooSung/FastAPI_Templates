# Scraping API server

A simple Web scraping API server built with FastAPI.

The main aim of this API server is to parse the [OpenGraph](https://ogp.me/) of the given web page by scraping the web page.

## Instructions

0. Set up virtualenv if required.
1. Install poetry
2. Install lock dependencies: `poetry install`
3. Export requirements.txt from poetry: `sh export_requirements_txt_from_poetry.sh`
4. Install pip dependencies: `pip install -r requirements.txt`
5. Run the server with Host and Port: `sh start.sh 0.0.0.0:8080`
