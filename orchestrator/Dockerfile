FROM python:3.11-slim

WORKDIR /app

ARG INCLUDE_TESTS=0

# Install minimal OS deps and upgrade pip
RUN apt-get update && apt-get install -y --no-install-recommends git \
 && rm -rf /var/lib/apt/lists/*

ENV PIP_ROOT_USER_ACTION=ignore
RUN pip install --no-cache-dir --upgrade pip

# Copy orchestrator code
COPY . /app/orchestrator

# Optionally include tests in the image (when not using bind-mount)
RUN if [ "$INCLUDE_TESTS" = "1" ]; then mkdir -p /app/tests && \
    if [ -d "/app/orchestrator/../tests" ]; then cp -r /app/orchestrator/../tests /app/; fi; \
    fi

# Install all orchestrator runtime deps (includes email-validator & Pillow)
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

ENV PYTHONUNBUFFERED=1
CMD ["uvicorn", "orchestrator.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
