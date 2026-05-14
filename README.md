# AI Processing Service

Worker service that consumes SQS messages, analyzes architecture diagrams with Gemini 2.0 Flash Vision, and sends structured reports to the report service.

## Responsibilities
- Consume messages from SQS queue (`diagram-analysis-queue`)
- Download diagram files from S3
- Convert PDFs to images (pdf2image + poppler)
- Analyze diagrams with Google Gemini 2.0 Flash Vision (LangChain)
- Validate LLM output with guardrails (Pydantic schema + sanitization)
- POST results to report-service
- Update upload status in upload-service

## AI Pipeline

```
SQS Message → Download S3 → (PDF→PNG) → Base64 → Gemini 2.0 Flash Vision → Guardrails → Report Service
```

## Guardrails
- JSON schema validation (Pydantic)
- Severity/Priority enum enforcement  
- String sanitization (trim, length cap)
- Retry on failure (2x)

## Environment Variables

| Variable | Description |
|---|---|
| `GOOGLE_API_KEY` | Google Gemini API key — obtenha em https://aistudio.google.com (required) |
| `AWS_REGION` | AWS region |
| `S3_BUCKET_NAME` | S3 bucket containing diagrams |
| `SQS_QUEUE_URL` | SQS queue URL to consume from |
| `UPLOAD_SERVICE_URL` | Internal URL of upload-service |
| `REPORT_SERVICE_URL` | Internal URL of report-service |
| `INTERNAL_SERVICE_TOKEN` | Token for service-to-service calls |

## Running locally

```bash
cp .env.example .env
# Edit .env — GOOGLE_API_KEY is required

pip install -r requirements.txt
python -m src.worker
```

## Running tests

```bash
pytest tests/ -v --cov=src
```
