# Build stage
FROM python:3.10-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /app

# Copy only requirements first to leverage Docker cache
COPY src/pyproject.toml .

# Install uv and dependencies
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    uv pip install --system -e ".[dev]" && \
    rm -rf ~/.cache/uv

# Final stage
FROM python:3.10-slim

ENV PATH="/root/.local/bin:${PATH}"
ENV PYTHONUNBUFFERED=1
ENV AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION:-us-east-2}

WORKDIR /app

# Copy only necessary files from builder
COPY --from=builder /usr/local/lib/python3.10/site-packages/ /usr/local/lib/python3.10/site-packages/
COPY src/ .

# Add AWS credentials script
COPY --chmod=755 <<-"EOF" /usr/local/bin/docker-entrypoint.sh
#!/bin/bash
set -e

if [ -n "$AWS_ACCESS_KEY_ID" ] && [ -n "$AWS_SECRET_ACCESS_KEY" ]; then
    mkdir -p ~/.aws
    echo "[default]" > ~/.aws/credentials
    echo "aws_access_key_id = $AWS_ACCESS_KEY_ID" >> ~/.aws/credentials
    echo "aws_secret_access_key = $AWS_SECRET_ACCESS_KEY" >> ~/.aws/credentials
    if [ -n "$AWS_SESSION_TOKEN" ]; then
        echo "aws_session_token = $AWS_SESSION_TOKEN" >> ~/.aws/credentials
    fi
fi

exec python -m notebooks.outsmarting_sagemaker_execute "$@"
EOF

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
