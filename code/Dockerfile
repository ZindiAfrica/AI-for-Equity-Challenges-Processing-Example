FROM python:3.10-slim

ENV PATH="/root/.local/bin:${PATH}"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /app

# Copy project configuration
COPY pyproject.toml .

# Install uv and Python dependencies
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    uv pip install --system -e ".[dev]" && \
    rm -rf ~/.cache/uv && \
    echo 'export PATH="/root/.local/bin:$PATH"' >> /etc/profile

# Copy the application code
COPY notebooks/ notebooks/

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION:-us-east-2}

# Add script to handle AWS credentials
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
# Configure AWS credentials if provided via environment variables\n\
if [ -n "$AWS_ACCESS_KEY_ID" ] && [ -n "$AWS_SECRET_ACCESS_KEY" ]; then\n\
    mkdir -p ~/.aws\n\
    echo "[default]" > ~/.aws/credentials\n\
    echo "aws_access_key_id = $AWS_ACCESS_KEY_ID" >> ~/.aws/credentials\n\
    echo "aws_secret_access_key = $AWS_SECRET_ACCESS_KEY" >> ~/.aws/credentials\n\
    if [ -n "$AWS_SESSION_TOKEN" ]; then\n\
        echo "aws_session_token = $AWS_SESSION_TOKEN" >> ~/.aws/credentials\n\
    fi\n\
fi\n\
\n\
# Execute the main script\n\
exec python -m notebooks.outsmarting_sagemaker_execute "$@"' > /usr/local/bin/docker-entrypoint.sh \
    && chmod +x /usr/local/bin/docker-entrypoint.sh

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
