FROM python:3.14-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app
COPY services/order-service/*.py ./
RUN python -m unittest -v
HEALTHCHECK --interval=5s --timeout=3s --start-period=5s --retries=3 \
  CMD ["python", "-c", "import urllib.request; response = urllib.request.urlopen('http://127.0.0.1:8080/health', timeout=2); raise SystemExit(response.status != 200)"]
ENTRYPOINT ["python", "main.py"]
