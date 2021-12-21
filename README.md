<div align="center">
<img src="https://user-images.githubusercontent.com/37064567/145668148-0de33ec5-7cbb-486e-be9a-b2fbe047e36a.jpg" title="cover image" width="400">
</div>

# teamaya
## What's teamaya?
- "teamaya" is a make-up word, teamaya = team + maya.
    - "team" means to let an animal pull and carry something.
    - "maya" means a cat in Okinawan dialect.
- Integrate and transfer data in spreadsheets to Google Cloud Platform and store data in GCP.

## Data integration
- Input: Spreadsheets
- Output: BigQuery in Google Cloud Platform
- [README.md](./teamaya/README.md)

### Starting the container
```bash
# clone
git clone https://github.com/masatakashiwagi/teamaya.git
cd teamaya/workflow

# build
docker compose build

# run
docker compose up -d digdag
```

### Access UI
You can access localhost in your environment. → http://localhost:65432/
