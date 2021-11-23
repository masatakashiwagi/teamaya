## Data integration
### Embulk
- Embulk is bulk data loader and perform the data transfer process.
- Transfer the data in the spreadsheets to the BigQuery Data Warehouse.

### Starting the container
- Start embulk container services in the background of the local environment.

```bash
cd embulk
docker compose up -d embulk
```

### Run the container
- Run the liquid file under the directory `config/`.

```bash
# dry-run
docker exec embulk sh /embulk/bin/embulk preview -b bundle config/spreadsheet/export_hab_purchase_amount.yml.liquid

# production-run
docker exec embulk sh /embulk/bin/embulk run -b bundle config/spreadsheet/export_hab_purchase_amount.yml.liquid
```

### Results
- You can confirm that a new table has been created in the dataset specified (=`purchase_amount_source_spreadsheets`) in the BigQuery `teamaya-8131` project.

## Notes.
- The project and dataset must have been created in GCP beforehand.
    - project: teamaya-8131
    - dataset: purchase_amount_source_spreadsheets
- You need to set the environment variables.
    - SPREADSHEETS_TABLE: Spreadsheets file URL
        - `export SPREADSHEETS_TABLE=<URL>`
    - GCP_SERVICE_JSON: Credential json file for service account.
        - `export GCP_SERVICE_JSON=/root/.gcp/teamaya.json`