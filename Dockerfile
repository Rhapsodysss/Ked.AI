# Dockerfile
FROM python:3.11-slim

# Minimal deps
RUN pip install --no-cache-dir flask

# Buat user non-root
RUN useradd -m -s /bin/bash sandboxuser
USER sandboxuser

WORKDIR /home/sandboxuser/app
COPY sandbox_api.py .

EXPOSE 5001

# Default: gunakan env SANDBOX_TOKEN untuk auth
CMD ["python", "sandbox_api.py"]
