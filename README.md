# Clan DB API

This is a FastAPI service deployed on Google Cloud Run with Cloud SQL (PostgreSQL) integration and Secret Manager for secure configuration.

---

## 🚀 Prerequisites

1. **Enable Required GCP APIs:**

```bash
gcloud services enable run.googleapis.com sqladmin.googleapis.com secretmanager.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com
```

2. **Set Your GCP Project and Region:**

```bash
gcloud config set project [YOUR_PROJECT_ID]
gcloud config set run/region us-central1
```

3. **Authenticate gcloud (if needed):**

```bash
gcloud auth login
```

---

## 🛠️ Secret Manager Setup

1. **Create Secret for Database URL:**

```bash
echo "postgresql+psycopg2://[USERNAME]:[ENCODED_PASSWORD]@/[DB_NAME]?host=/cloudsql/[INSTANCE_CONNECTION_NAME]" \
| gcloud secrets create DATABASE_URL --data-file=-
```

2. **Grant Access to Cloud Run Service Account:**

```bash
gcloud projects add-iam-policy-binding [PROJECT_ID] \
--member=serviceAccount:[PROJECT_NUMBER]-compute@developer.gserviceaccount.com \
--role=roles/secretmanager.secretAccessor
```

---

## 💾 Cloud SQL IAM Setup

1. **Grant Cloud SQL Client Role to Service Account:**

```bash
gcloud projects add-iam-policy-binding [PROJECT_ID] \
--member=serviceAccount:[PROJECT_NUMBER]-compute@developer.gserviceaccount.com \
--role=roles/cloudsql.client
```

---

## 🐳 Docker & Build Setup

Make sure your repo includes the following files:
- `main.py` (FastAPI app)
- `Dockerfile`
- `requirements.txt`
- `cloudbuild.yaml`

### Dockerfile Example:

```Dockerfile
FROM python:3.11

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### cloudbuild.yaml:

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
        '--set-secrets', 'DATABASE_URL=DATABASE_URL:latest',
        '--add-cloudsql-instances', '[INSTANCE_CONNECTION_NAME]'
      ]
```

---

## 🔁 Deploy

Submit build manually or set a trigger via GitHub/Cloud Source Repositories.

```bash
gcloud builds submit --config cloudbuild.yaml
```

---

## ✅ Test API

POST:

```bash
curl -X POST https://[SERVICE_URL]/clans \
-H "Content-Type: application/json" \
-d '{"name": "Shadow Ninjas", "region": "Asia"}'
```

GET:

```bash
curl https://[SERVICE_URL]/clans
```

---

## 📌 Notes

- Replace placeholders: `[PROJECT_ID]`, `[PROJECT_NUMBER]`, `[USERNAME]`, `[ENCODED_PASSWORD]`, `[DB_NAME]`, `[INSTANCE_CONNECTION_NAME]`, `[SERVICE_URL]`
- Encode special characters in passwords for URLs.
- Always redeploy after code or environment changes.
