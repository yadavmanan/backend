FROM python:3.12-slim

WORKDIR /app

# Install system deps needed by PyMuPDF and other native packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libffi-dev && \
    rm -rf /var/lib/apt/lists/*

COPY data/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Remove the local virtualenv if accidentally copied
RUN rm -rf env/ __pycache__/

EXPOSE 5050

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5050"]
