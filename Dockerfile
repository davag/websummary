FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Set the environment variable to production
ENV FLASK_ENV=production

EXPOSE 5000

CMD ["python", "webapp.py"] 