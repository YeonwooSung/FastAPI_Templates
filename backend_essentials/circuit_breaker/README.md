# Scraper service with Circuit Breaker

Use aiobreaker for circuit breaker.

The caller service will call the scraper service to get the data, and the callee service will use web scraping to get the data.
The caller will use the circuit breaker to protect the service from the callee service failure.
