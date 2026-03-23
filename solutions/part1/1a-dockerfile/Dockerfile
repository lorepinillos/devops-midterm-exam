# FIX 1: Use slim variant to reduce image size (best practice)
FROM python:3.13-slim

LABEL org.opencontainers.image.source=https://github.com/oriolrius/devops-midterm-exam

# Install uv package manager (project uses uv, not pip)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# FIX 2: Copy only needed files instead of everything (COPY . . includes unnecessary files)
COPY pyproject.toml README.md ./
COPY src/ src/

# FIX 3: Use uv with pyproject.toml instead of pip with requirements.txt
# (project uses uv and pyproject.toml, requirements.txt does not exist)
RUN uv pip install --system .

# FIX 4: Remove hardcoded secret — secrets must never be baked into images
# ENV API_KEY=sk-secret-key-do-not-share  ← removed, pass via env at runtime

EXPOSE 8000

# FIX 5: Use exec form and the installed console script entry point instead of
# shell form calling src/main.py directly (entry point is defined in pyproject.toml)
CMD ["mock-openai-api"]
