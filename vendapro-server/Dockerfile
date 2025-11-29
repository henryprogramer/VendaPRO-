FROM python:3.11
WORKDIR /server
COPY . .
RUN pip install -r requirements.txt
CMD ["bash", "-c", "uvicorn fastapi_app.main:app --host 0.0.0.0 --port 8000"]
