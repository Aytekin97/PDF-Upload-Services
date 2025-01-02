import boto3
from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import JSONResponse
from botocore.exceptions import NoCredentialsError
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI()
app.add_middleware(HTTPSRedirectMiddleware, max_body_size=50 * 1024 * 1024)  # 50 MB

# Allowed MIME types
ALLOWED_MIME_TYPES = [
    "application/pdf",  # PDF
    "application/msword",  # .doc
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"  # .docx
]

# AWS S3 Configuration
AWS_ACCESS_KEY = "YOUR_AWS_ACCESS_KEY"
AWS_SECRET_KEY = "YOUR_AWS_SECRET_KEY"
BUCKET_NAME = "YOUR_BUCKET_NAME"

# S3 Client
s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY
)

@app.post('/api/upload')
async def upload_pdf(company_name: str = Form(...), file: UploadFile = Form(...)):
    try:
        logger.info(f"Uploading {file.filename} for {company_name}")
        
        # Validate file type
        if file.content_type not in ALLOWED_MIME_TYPES:
            return JSONResponse(
                status_code=400,
                content={"message": "Invalid file type. Only PDF, DOC, and DOCX files are allowed."}
            )

        # Define the S3 file key
        s3_file_key = f"{company_name}/{file.filename}"

        # Upload the file to S3
        s3_client.upload_fileobj(
            file.file,
            BUCKET_NAME,
            s3_file_key,
            ExtraArgs={"ContentType": file.content_type}
        )

        # Return success response with S3 file path
        return JSONResponse(
            status_code=200,
            content={
                "message": "File uploaded successfully",
                "file_url": f"https://{BUCKET_NAME}.s3.amazonaws.com/{s3_file_key}"
            }
        )
    except NoCredentialsError:
        return JSONResponse(
            status_code=500,
            content={"message": "AWS credentials not available"}
        )
    except Exception as e:
        logger.error(f"Failed to upload {file.filename}: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"message": str(e)}
        )
    

# Run the app
# To run: uvicorn filename:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)