FROM python:3.11-slim

WORKDIR /app

COPY topic-scout/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY shared/ /app/shared/
COPY topic-scout/ /app/

EXPOSE 8000

CMD ["python", "agent.py"]
