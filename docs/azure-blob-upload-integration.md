# Azure Blob Upload Integration: Design, Setup & Usage

## Executive Summary
We added first-class Azure Blob Storage support for large PDF uploads.  
The frontend can now toggle between:

* **Local multipart uploads** (default)  
* **Direct-to-Azure uploads** (new)

When Azure mode is enabled:

1. Frontend requests a short-lived **SAS URL** from the backend.  
2. Browser PUTs the file bytes straight to Azure (`x-ms-blob-type: BlockBlob`).  
3. Frontend notifies the backend via `/uploads/register`.  

The backend then downloads the blob, stores it locally, and—if the file is larger than 40 MB—triggers the existing **chunking pipeline**. This removes upload bottlenecks, allowing ~1 GB, multi-thousand-page PDFs without sending file bytes through the API server.

---

## What Changed

| Layer      | Key Additions / Edits |
|------------|-----------------------|
| **Frontend** | • `VITE_API_URL` and `VITE_UPLOAD_MODE` env flags in `src/services/api.ts`.<br>• New Azure upload flow (SAS → PUT → register). |
| **Backend** | • New settings in `app/core/config.py` (`STORAGE_MODE`, Azure creds, TTL).<br>• Dependency `azure-storage-blob>=12.21.0`.<br>• Service `app/services/azure_storage.py` (SAS generation & streaming download).<br>• Endpoints `app/api/endpoints/uploads.py`.<br>• Router wired in `app/api/api.py`. |
| **Infra** | • `render.yaml` updated with Azure env vars & `VITE_UPLOAD_MODE`. |

No DB schema changes—existing `DocumentStatus` values are reused.

---

## Environment & Deployment

### Backend `.env`
```
STORAGE_MODE=azure           # or 'local'
AZURE_STORAGE_ACCOUNT_NAME=<your_account>
AZURE_STORAGE_ACCOUNT_KEY=<your_key>
AZURE_STORAGE_CONTAINER_NAME=<your_container>
AZURE_SAS_TTL_MINUTES=60
VISION_AGENT_API_KEY=...
OPENAI_API_KEY=...
```

### Frontend (Vite)
```
VITE_API_URL=https://your-backend
VITE_UPLOAD_MODE=azure       # or 'local'
```

### Render
`render.yaml` already contains placeholders (`sync: false`).  
Set the Azure secrets in the Render dashboard and keep `VITE_UPLOAD_MODE=azure`.

---

## API Reference (New)

### `POST /api/v1/uploads/azure-sas`
Request
```json
{
  "filename": "file.pdf",
  "content_type": "application/pdf",
  "size": 1048576
}
```
Response
```json
{
  "uploadUrl": "https://<acct>.blob.core.windows.net/<container>/<blob>?<sas>",
  "blobUrl": "https://<acct>.blob.core.windows.net/<container>/<blob>",
  "expiresAt": "2025-08-10T12:00:00Z"
}
```

### `POST /api/v1/uploads/register`
Request
```json
{
  "blob_url": "https://<acct>.blob.core.windows.net/<container>/<blob>",
  "filename": "file.pdf",
  "size": 1048576
}
```
Response → standard **Document** object.

**Notes**

* Use `uploadUrl` for the PUT; supply `x-ms-blob-type: BlockBlob`.
* Files > 40 MB are flagged `is_chunked = true`; backend status transitions  
  `PENDING → CHUNKING → PENDING` (ready to parse) automatically.

---

## Example Flows

### Frontend (Azure mode)
1. `POST /uploads/azure-sas`
2. `PUT` file to `uploadUrl`
3. `POST /uploads/register` with `blobUrl`

### cURL Manual Test
```bash
# 1. Get SAS
curl -s -X POST "$API/api/v1/uploads/azure-sas" \
  -H "Content-Type: application/json" \
  -d '{"filename":"big.pdf","content_type":"application/pdf","size":1048576}'

# 2. Upload to Azure
curl -X PUT "$UPLOAD_URL" \
  -H 'x-ms-blob-type: BlockBlob' \
  -H 'Content-Type: application/pdf' \
  --data-binary @big.pdf

# 3. Register
curl -s -X POST "$API/api/v1/uploads/register" \
  -H "Content-Type: application/json" \
  -d '{"blob_url":"'$BLOB_URL'","filename":"big.pdf","size":1048576}'
```

---

## Operational Notes

* **Large-file threshold**: `>40 MB` triggers chunking (45-page chunks).
* **Background tasks**
  * Download blob → local.
  * Decide small vs. large.
  * For large, spawn `process_large_document_async`.
* Standard parse → process → review → export flows unchanged.
* CORS only affects backend endpoints; direct PUT goes to Azure.

---

## How to Test

1. **Local**
   1. Fill `.env` (see above) and set `STORAGE_MODE=azure`.
   2. `pip install -r backend/requirements.txt`.
   3. Run backend & frontend (`VITE_UPLOAD_MODE=azure`).
   4. Upload small (<40 MB) and large (>40 MB) PDFs; confirm statuses and chunk counts.

2. **Render**
   1. Deploy latest `main` branch (render.yaml).
   2. Populate Azure secrets in backend service.
   3. Ensure frontend env vars point to backend and `VITE_UPLOAD_MODE=azure`.
   4. Repeat upload tests.

---

## Future Enhancements

* Per-operation SAS: write-only for browser, read-only for backend.
* Retry logic & metrics for downloads/chunking.
* Optional new status `DOWNLOADING` (would require DB migration).

---

## References

1. Azure Blob Storage Python SDK: <https://learn.microsoft.com/azure/storage/blobs/storage-quickstart-blobs-python>  
2. Shared Access Signatures: <https://learn.microsoft.com/azure/storage/common/storage-sas-overview>  
3. `BlobSasPermissions` docs: <https://learn.microsoft.com/python/api/azure-storage-blob/azure.storage.blob.blobsaspermissions>  
4. FastAPI BackgroundTasks: <https://fastapi.tiangolo.com/advanced/background-tasks/>
