# GeoIP Server

A FastAPI based server that runs the GeoIP lookup service.
Retrieves the geolocation information for a given IP address.

## Instructions

0. Set up virtualenv if required.
1. Install poetry
2. Install lock dependencies: `poetry install`
3. Export requirements.txt from poetry: `sh export_requirements_txt_from_poetry.sh`
4. Install pip dependencies: `pip install -r requirements.txt`
5. Run the server: `sh start.sh`
