### Your First Pipeline

Use `copier` to generate a new pipeline from the template.

```sh
# Navigate to templates directory
cd path/to/templates

# Install copier
pip install copier

# Generate new pipeline from template
copier copy basic-pipeline-template basic-pipeline

# Zip the pipeline
zip -r basic-pipeline.zip basic-pipeline
```

Your first pipeline are ready to be registered to GLLM Backend!

```sh
# Register the pipeline to GLLM Backend
curl --request POST \
  --url {BE_URL}/register-pipeline-plugin \
  --header 'Content-Type: multipart/form-data' \
  --form 'zip_file=@/path_to_pipeline/basic-pipeline.zip'

# Test send message to application
curl -X POST "{BE_URL}/message" \
  -F "chatbot_id=basic-pipeline-app" \
  -F "user_id=username" \
  -F "message=Hello world" \
  --no-buffer

# Unregister the pipeline from GLLM Backend
curl --request POST \
  --url {BE_URL}/unregister-pipeline-plugin \
  --header 'Content-Type: application/json' \
  --data '["basic-pipeline"]'
```
