# Clan API - GCP Deployment Guide

This README provides a step-by-step guide to deploy a FastAPI-based API on Google Cloud Run using Cloud Build, Secret Manager, and Cloud SQL for PostgreSQL.

---

## 🚀 Prerequisites

Ensure the following are installed and configured:

```bash
# Install Google Cloud SDK
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init
```

---

## 🔧 Enable Required GCP Services

```bash
gcloud services enable run.googleapis.com     cloudbuild.googleapis.com     secretmanager.googleapis.com     sqladmin.googleapis.com     artifactregistry.googleapis.com
```

---

## 🗃️ Create PostgreSQL Instance on Cloud SQL

```bash
gcloud sql instances create <INSTANCE_ID>     --database-version=POSTGRES_14     --tier=db-f1-micro     --region=us-central1
```

Create the database:

```bash
gcloud sql databases create <DB_NAME>     --instance=<INSTANCE_ID>
```

Create a user:

```bash
gcloud sql users create <DB_USER>     --instance=<INSTANCE_ID>     --password=<DB_PASSWORD>
```

---

## 🔐 Create Secrets

Store your PostgreSQL connection string in Secret Manager. Be sure to URL-encode any special characters in the password.

```bash
echo "postgresql+psycopg2://<DB_USER>:<ENCODED_PASSWORD>@/<DB_NAME>?host=/cloudsql/<PROJECT_ID>:<REGION>:<INSTANCE_ID>" | gcloud secrets create DATABASE_URL --data-file=-
```

Grant Secret Manager access to the Cloud Run service account:

```bash
gcloud projects add-iam-policy-binding <PROJECT_ID>     --member="serviceAccount:<PROJECT_NUMBER>-compute@developer.gserviceaccount.com"     --role="roles/secretmanager.secretAccessor"
```

---

## 🐳 Docker & Cloud Build

Ensure the following files exist in your repo:

- `Dockerfile`
- `cloudbuild.yaml`
- `main.py`
- `requirements.txt`

### Sample `cloudbuild.yaml`

```yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/clan-api', '.']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/clan-api']
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      [
        'run', 'deploy', 'clan-api',
        '--image', 'gcr.io/$PROJECT_ID/clan-api',
        '--platform', 'managed',
        '--region', 'us-central1',
        '--allow-unauthenticated',
        '--add-cloudsql-instances', '<PROJECT_ID>:us-central1:<INSTANCE_ID>',
        '--set-secrets', 'DATABASE_URL=DATABASE_URL:latest'
      ]
```

---

## 🚀 Deploy with Cloud Build

```bash
gcloud builds submit --project=<PROJECT_ID>
```

---

## ✅ Test the API

Use `curl` or Thunder Client:

```bash
curl -X POST https://<CLOUD_RUN_URL>/clans \
     -H "Content-Type: application/json" \
     -d '{"name": "Shadow Ninjas", "region": "Asia"}'
```

List:

```bash
curl https://<CLOUD_RUN_URL>/clans
```

---

## ✅ Trigger on Push

You can create a trigger in Cloud Build UI to automatically build and deploy when new commits are pushed to your repository.

---

## 📁 Notes

- Ensure your DB name matches exactly what’s in the connection string.
- Use Secret Manager instead of hardcoding passwords or URLs.
