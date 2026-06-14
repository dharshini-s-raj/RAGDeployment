FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY fastapi_app.py rag_core.py utils.py ./
COPY prompts ./prompts
EXPOSE 8000
CMD ["uvicorn", "fastapi_app:app", "--host", "0.0.0.0", "--port", "8000"]