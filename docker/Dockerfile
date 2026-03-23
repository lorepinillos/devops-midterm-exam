FROM python:3.13-slim

LABEL org.opencontainers.image.source=https://github.com/oriolrius/devops-midterm-exam
LABEL org.opencontainers.image.description="Mock OpenAI-compatible API for DevOps exam"
LABEL org.opencontainers.image.licenses=MIT

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy project files
COPY pyproject.toml README.md ./
COPY src/ src/

# Install the application
RUN uv pip install --system .

EXPOSE 8000

CMD ["mock-openai-api"]
