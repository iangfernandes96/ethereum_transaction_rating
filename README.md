---
title: Ethereum Transaction Rating Service
---

# Ethereum Transaction Rating Service

## Table of Contents

- [Prerequisites](#prerequisites)
- [Usage](#usage)
- [Assumptions/Optimizations](#assumptions/optimizations)
- [Testing](#testing)
- [Design](#design)
- [Load Test Results](#loadtestresults)
- [Further Improvements](#improvements)

## Prerequisites

You will need Docker and Docker Compose installed on your system. Additionally, ensure you have Python 3.12+ and the `make` tool installed.

## Usage

### Starting the Application

To get started with this project, follow these steps:

1. Open a terminal and navigate to the project folder.

2. Run `make start` to build and start the application server. This command will internally:
   - Create the necessary Docker containers.
   - Initialize the application.
   - Start the server.

3. With the application running, you can interact with the API endpoints:
   - **Login:** `POST http://localhost:8000/api/user/token`
   - **Get Latest Hashes:** `GET http://localhost:8000/api/transaction/latest-hashes`
   - **Get Old Hashes:** `GET http://localhost:8000/api/transaction/old-hashes`
   - **Get Transaction Rating:** `GET http://localhost:8000/api/transaction/rating?transaction_hash=<HASH>`

4. For interacting with the API, use tools like `curl`, Postman, or directly through a web browser for GET requests. 

5. To load test the API endpoints, run load tests with Locust by executing `make load-test`.



### Interacting with the Application
Please run `make start` in a terminal, and navigate to `http://localhost:8000/docs`, to view the documentation for this service.
To simulate a free user, enter `user` for the username, and `password` for the password when requesting for a token.
To simulate a paid user, enter `paid_user` for the username, and `password` for the password when requesting for a token.

1. To login, send a POST request to `/api/user/token`

2. To get the latest transaction hashes, send a GET request to `/api/transaction/latest-hashes`.

3. To retrieve historical transaction hashes, use the GET request to `/api/transaction/old-hashes`.

4. To check the rating of a transaction, send a GET request to `/api/transaction/rating` with the `transaction_hash` query parameter. You can pass any hash from the list of transaction hashes returned via either the `/latest-hashes` or the `/old-hashes` endpoint.

5. For performance and load testing, use Locust by running `make load-test`.

### Stopping the Application

1. Run `make stop` to stop the running Docker containers and clean up the environment.


## Assumptions/Optimizations
1. If a transaction has been given a rating by this service, I assumed that this rating does not change for subsequent calls with 
the same hash, and am hence caching it.
2. Latest transaction hashes are cached in Redis, to avoid making repeated calls to Alchemy. The transactions are cached for a duration
of 120 seconds currently, and are refreshed every 60 seconds, so as to enable testing for both user type flows. These values can be tweaked by editing the `LATEST_TXNS_TTL` and the `REFRESH_TXN_INTERVAL` values in `src/config.py` respectively.
3. When latest transactions are refreshed, the existing transactions are moved to another list of old transaction hashes (to enable testing the rating flow for a free user). If you want to test a successful rating flow when logged in as a free user, make an api call to `/api/transaction/old-hashes`, and pass any transaction hash from this list.

## Testing

1. Run `make test` to execute unit tests. This will:
   - Create a virtual environment if it doesn't exist.
   - Install necessary dependencies from `requirements_test.txt`.
   - Execute tests using `pytest`.

2. Run `make load-test` to open up a load testing GUI (Locust)
   - Starts the application server in detached mode.
   - Installs necessary dependencies, and locust
   - Executes locustfile
   - Open `http://localhost:8089` in a browser, to see the load test GUI and run load tests against the application.

## Design Overview

1. **FastAPI Application**
   - **Purpose:** Acts as the main server handling HTTP requests for Ethereum transaction ratings.
   - **Key Features:**
     - Exposes REST endpoints for login, retrieving transaction hashes and ratings.
     - Implements JWT authentication for protected endpoints.

2. **AlchemyClient**
   - **Purpose:** Interacts with the Alchemy API to fetch transaction and block information from the Ethereum network.
   - **Functionality:**
     - Retrieves transaction details by hash.
     - Retrieves block details by number.
     - Retrieves the latest block information.

3. **TransactionRedisManager**
   - **Purpose:** Manages transaction hashes and their ratings in Redis.
   - **Functionality:**
     - Stores and retrieves the latest and old transaction hashes.
     - Caches transaction ratings for efficient access.
     - Refreshes the list of transaction hashes periodically.

4. **Redis**
   - **Purpose:** Acts as a cache and message broker for transaction hashes and ratings.
   - **Key Components:**
     - Stores latest and old transaction hashes.
     - Caches transaction ratings to optimize performance.

5. **Utils**
   - **Purpose:** Utils that are used throughout the project.
   - **Key Components:**
     - Utility functions to convert str to hex, get block age, compute trust rating and refresh latest transactions in redis.

### Interaction

- **Initialization:**
  - On startup, `TransactionRedisManager` initializes the latest hashes and sets up periodic refreshes.
  - `AlchemyClient` interacts with the Ethereum network to fetch real-time data.

- **Handling Requests:**
  - **HTTP Requests:** Handled by FastAPI endpoints:
    - Retrieve latest and old transaction hashes.
    - Check transaction ratings.

- **Caching and Performance:**
  - Redis is used to cache transaction data and ratings to reduce the load on the Ethereum API and improve response times.


## Load test results

I ran a load test for this application locally, using Locust, and have attached the results generated as part of these tests, in the `load-test-results` folder. These tests were run on a Macbook M1 Pro, with 16GB RAM. The server set up was `1` FastAPI worker process. 
The number of maximum concurrent users was set to `1000 users`, with a ramp-up of `10 users/second`.


## Improvements
- **More robust error-handling**: Currently, I have only implemented some basic error-handling, and have not accounted for inter-service failures, but this would be necessary in a production environment, in order to handle such failures gracefully.
- **Load balancer**: This backend service could potentially sit behind a load balancer like Nginx/Kong, allowing for seamless load-balancing between running containers. A Load balancer can also handle some/all parts of AuthN/AuthZ, thereby offloading that responsibility from the backend service.
- **Logging**: A common logger, with various log levels would be good to have, as it will enable easier debugging. These logs can be exported to ELK/Clickhouse, and can be queried via a dashboard on Grafana.
- **Monitoring**: In order to monitor the health and performance metrics of this application, we can make use of Prometheus, to export application metrics to an endpoint, which can be queried via Grafana, in order to build dashboards and alerts over these metrics.