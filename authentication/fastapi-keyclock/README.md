# Securing FastAPI with Keycloak

## Virtual env
```bash
make virtual
```

## Running the app
```bash
make run
```

## Run Keycloak
```bash
make keycloak
```

## Get Token
```bash
make token
```
By running the above command, you will get a token that you can use to access the secure endpoint.
This token will be used for the `/secure-data` endpoint.

## Sample calls

Replace the `<YOUR_TOKEN>` with the token you got from the `make token` command.
```bash
export TOKEN=<YOUR_TOKEN>

curl http://127.0.0.1:8000/secure-data \
--header "Authorization: Bearer ${TOKEN}"
```
