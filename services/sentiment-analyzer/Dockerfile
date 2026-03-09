FROM python:3.11-slim

WORKDIR /app

COPY sentiment-analyzer/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY shared/ /app/shared/
COPY sentiment-analyzer/ /app/

EXPOSE 8000

CMD ["python", "agent.py"]
