# waldur-metrics-exporter

## Available commands

- manage.py migrate
- manage.py update_country_limits
- manage.py update_country_usage
- manage.py update_country_quotas

## Available env variables

- START_YEAR
- METRICS_DB_NAME
- METRICS_DB_USER
- METRICS_DB_PASSWORD
- METRICS_DB_HOST
- METRICS_DB_PORT

- SOURCE_DB_NAME
- SOURCE_DB_USER
- SOURCE_DB_PASSWORD
- SOURCE_DB_HOST
- SOURCE_DB_PORT

# Deployment in Kubernetes

1. Install PostgreSQL release:

    ```bash
    helm repo add bitnami https://charts.bitnami.com/bitnami
    helm install postgresql-waldur-metrics-exporter bitnami/postgresql --version 12.2.8 -f k8s/psql-values.yaml -n puhuri-services
    ```

2. Load Configmap with country quotas. Make sure that format of the CSV file is correct.

   ```bash
   kubectl create configmap country-quotas --from-file=country-quotas.csv=country-quotas.csv -n puhuri-services
   ```

3. Prepare DB structure

    ```bash
    kubectl apply -f k8s/tracker_db_init.yaml -n puhuri-services
    ```

4. Deploy aai_tracker cron jobs

    ```bash
    kubectl apply -f k8s/tracker_cron_limits.yaml -n puhuri-services
    kubectl apply -f k8s/tracker_cron_usage.yaml -n puhuri-services
    kubectl apply -f k8s/tracker_cron_quotas.yaml -n puhuri-services
    ```

