FROM python:3.11-slim

WORKDIR /app

COPY editor/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY shared/ /app/shared/
COPY editor/ /app/

EXPOSE 8000

CMD ["python", "agent.py"]
