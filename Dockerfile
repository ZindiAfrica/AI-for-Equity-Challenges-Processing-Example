FROM 763104351884.dkr.ecr.us-east-2.amazonaws.com/pytorch-training:2.0.0-gpu-py310

# Install additional dependencies
RUN pip install --no-cache-dir \
    pandas \
    scikit-learn \
    boto3 \
    sagemaker

# Set up working directory
WORKDIR /opt/ml/code

# Copy the scripts from notebooks directory
COPY notebooks/outsmarting_data_prep.py .
COPY notebooks/outsmarting_train.py .
COPY notebooks/outsmarting_eval.py .
COPY notebooks/outsmarting_predict.py .
COPY notebooks/outsmarting_sagemaker_execute.py .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION:-us-east-2}

# Add script to handle AWS credentials
COPY <<EOF /usr/local/bin/docker-entrypoint.sh
#!/bin/bash
set -e

# Configure AWS credentials if provided via environment variables
if [ -n "$AWS_ACCESS_KEY_ID" ] && [ -n "$AWS_SECRET_ACCESS_KEY" ]; then
    mkdir -p ~/.aws
    echo "[default]" > ~/.aws/credentials
    echo "aws_access_key_id = $AWS_ACCESS_KEY_ID" >> ~/.aws/credentials
    echo "aws_secret_access_key = $AWS_SECRET_ACCESS_KEY" >> ~/.aws/credentials
    if [ -n "$AWS_SESSION_TOKEN" ]; then
        echo "aws_session_token = $AWS_SESSION_TOKEN" >> ~/.aws/credentials
    fi
fi

# Execute the main script
exec python outsmarting_sagemaker_execute.py "$@"
EOF

RUN chmod +x /usr/local/bin/docker-entrypoint.sh

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
