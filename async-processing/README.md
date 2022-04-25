# async-processing
## What's this?
- Task queue applications for asynchronous processing of machine learning with FastAPI and RabbitMQ.
- The producer generates task as a message and sends it to a queue (RabbitMQ). The consumer then receives the queue, processes it to build a machine learning model, and when processing is complete, the message is sent again through the queue to the producer side.
- Database is not used in this case.

## Components
- **Producer**: FastAPI provides APIs to post ML task
- **Broker**: RabbitMQ is a message broker
- **Consumer**: Task executer
- **Storage**: S3 is the result stores which store machine learning model
- Containerize FastAPI, RabbitMQ, and Consumer with Docker.

## Architecture
![async-apps1](https://user-images.githubusercontent.com/37064567/163514038-41484608-3590-4887-af77-25514d1d0843.png)

## Usage
### Start/Stop containers
```docker
# clone
git clone https://github.com/masatakashiwagi/teamaya.git
cd teamaya/async-processing

# build
docker compose build

# start
docker compose up

# stop: Stops a running container, but does not delete it
docker compose stop

# down: Delete a container network volume image created with "docker compose up" command
docker compose down
```

### Access FastAPI and RabbitMQ endpoint
```bash
# FastAPI
http://localhost:5000/docs

# RabbitMQ
http://localhost:15672/
Username: guest
Password: guest
```

### Environment Variables
This is a `.env` file settings.
```
# .env
S3_BUCKET_NAME=<Your S3 bucket name>
S3_PATH_NAME=<Your dataset path to train machine learning model>
S3_MODEL_PATH_NAME=<Your model path to save machine learning model>
```

## References
- [FastAPI](https://fastapi.tiangolo.com/)
- [RabbitMQ](https://www.rabbitmq.com/)
    - [RabbitMQ Tutorials](https://github.com/rabbitmq/rabbitmq-tutorials)
- [Asynchronous message-based communication](https://docs.microsoft.com/en-us/dotnet/architecture/microservices/architect-microservice-container-applications/asynchronous-message-based-communication)
