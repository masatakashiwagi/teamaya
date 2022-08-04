#!/bin/sh

echo " =========== "
echo " Embulk processing start... "

echo "Start embulk container services in the background of the local environment."
docker compose up -d embulk

echo "production-run"
docker exec embulk sh /bin/embulk run -b embulk/bundle embulk/task/spreadsheet/export_hab_purchase_amount.yml.liquid

echo "Finish data sync processing."