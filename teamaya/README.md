## Data integration
### Digdag
- Digdag is a simple workflow engine that helps you to build, run, schedule.

### Starting the container
- Start digdag and its dependency postgresql container services in the background of the local environment.
- Build the Docker image and start the digdag service with `docker compose up` command.

```bash
cd teamaya/workflow
docker compose build
docker compose up -d digdag
```

### Access UI
You can access localhost in your environment.
`http://localhost:65432/`
