This document provides troubleshooting steps to follow in situations where inventory-api does not start.
1. Verify that inventory-api is configured with the same PostgreSQL password as inventory-db if inventory-api reports an error.
2. Verify that inventory-db is healthy using docker compose ps, as inventory-api depends on inventory-db, meaning that the database needs to be ready before the API can connect to it.
3. Review the logs using the following commands and troubleshoot accordingly if either service is not running or is unhealthy:
docker compose logs inventory-db
and/or
docker compose logs inventory-api
