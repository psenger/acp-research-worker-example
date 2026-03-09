FROM python:3.11-slim

WORKDIR /app

COPY summarizer/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY shared/ /app/shared/
COPY summarizer/ /app/

EXPOSE 8000

CMD ["python", "agent.py"]
