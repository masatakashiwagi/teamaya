## Data integration
### Embulk
- Embulk is bulk data loader and perform the data transfer process.
- Transfer the data in the spreadsheets to the BigQuery Data Warehouse.

### Starting the container
- Start embulk container services in the background of the local environment.

```bash
cd teamaya/workflow
docker compose up -d embulk
```

### Run the container
- Run the liquid file under the directory `task/`.

```bash
# dry-run
docker exec embulk sh /bin/embulk preview -b embulk/bundle embulk/task/spreadsheet/export_hab_purchase_amount.yml.liquid

# production-run
docker exec embulk sh /bin/embulk run -b embulk/bundle embulk/task/spreadsheet/export_hab_purchase_amount.yml.liquid
```

### Results
- You can confirm that a new table has been created in the dataset specified (=`purchase_amount_source_spreadsheets`) in BigQuery `teamaya-8131` project.

## Notes.
- The project and dataset must have been created in GCP beforehand.
    - project: `teamaya-8131`
    - dataset: `purchase_amount_source_spreadsheets`
- You need to set the environment variables to `.env` file.
    - SPREADSHEETS_TABLE: Spreadsheets file URL
        - `SPREADSHEETS_TABLE=<URL>`
    - GCP_SERVICE_JSON: Credential json file for service account.
        - `GCP_SERVICE_JSON=<credential json file path>`