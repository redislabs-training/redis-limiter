# Redis Rate Limiter

A simple server-side rate limiter using Redis Triggers and Javascript Functions.

This rate limiter limits the number of requests a user token API can do per minute.
It implements the following logic: the API gateway checks the current calls in a specific minute.

```
GET [user-api-key]:[current minute number]
```

If the counter is under a threshold, increase it using the following transaction, otherwise add the API token to the Redis Stream `exceeding` and exit.

```
MULTI
INCR [user-api-key]:[current minute number]
EXPIRE [user-api-key]:[current minute number] 59
QUEUED
EXEC
```

## Setup of the demo

This is a server-side rate limiter written in JavaScript and uses triggers to detect events on the API counters. 

You can test this proof-of-concept using the latest Docker image including the "Triggers and Functions" feature. Start a container as follows:

```
docker run -p 6379:6379 redislabs/redisgears:edge
```

And import the Javascript library into the Redis Server:

```
redis-cli -x TFUNCTION LOAD REPLACE < ./limiter.js
```

A load generator is provided and written in Python. Now prepare the Python environment:

```
python3 -m venv limiter
source limiter/bin/activate
pip install redis
```

And start the demo as follows:

```
python3 generator.py -P 6379 -c 3 -t 100
```

## Use of Triggers

This proof-of-concept implements two triggers:

- A trigger is subscribed to the API token counters. Custom implementation can be added, such as storing the counter in a Redis Time Series for subsequent analytics
- Another trigger is subscribed to the Stream `exceeding` and logs the data received. Custom implementation can be added to the trigger


