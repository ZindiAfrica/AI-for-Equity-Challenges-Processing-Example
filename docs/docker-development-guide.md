# Local Development with Docker

This guide covers how to develop and run the ML pipeline using Docker containers. This approach is suitable if you:
- Want a consistent development environment
- Need to test the exact environment that will run in production
- Prefer isolation from your local system

## Prerequisites

1. Docker installed and running
2. AWS credentials ready to inject into container
3. Basic understanding of Docker commands

## Development Setup

1. Configure AWS credentials as environment variables:
```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_REGION=us-east-2
```

2. Build the development container:
```bash
docker compose build
```

3. Start the development container:
```bash
docker compose up dev
```

4. In a new terminal, exec into the running container:
```bash
docker compose exec dev bash
```

5. Inside the container, your code is mounted at /app and AWS credentials are automatically injected from your environment.

6. Push to ECR (if needed):
```bash
./build_and_push.sh
```

## Running the Pipeline

1. From inside the container, you can run:
```bash
python build_and_run_aws.py
```

2. For debugging, use the debug entry point:
```bash
python debug_entry.py
```

## Building for Production

1. Build the production image:
```bash
./build_and_push.sh
```

This will:
- Build the Docker image
- Tag it appropriately
- Push to Amazon ECR

## Container Structure

The development container includes:
- All runtime dependencies
- Development tools (ruff, pytest, etc.)
- AWS credentials injection
- Code mounted as a volume

The production container includes:
- Only runtime dependencies
- Optimized for size and security
- No development tools
- Code copied into image

## Monitoring

Monitor containers using:
1. `docker compose ps` - Container status
2. `docker compose logs` - Container logs
3. AWS Console for pipeline jobs
