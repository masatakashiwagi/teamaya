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

### Set up projects and Run workflow.
- After creating a new project, write a workflow and run it to transfer the data to BigQuery by Embulk.

<img width="1422" alt="digdag-img0" src="https://user-images.githubusercontent.com/37064567/145683457-5afa8e48-411f-44be-bb63-dbd17226500f.png">
