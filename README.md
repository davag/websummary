# websummary

A web application that generates summaries of websites using AI.

## Local Development with Docker

### Prerequisites
- Docker Desktop installed and running
- OpenAI API key

### Building and Running with Docker

1. Build the Docker image:
```
docker build -t websummary-app .

2. Run the container:
```bash
docker run -p 5000:5000 --env-file .env websummary-app
```

Or, if you prefer to pass the API key directly:
```bash
docker run -p 5001:5000 --name websummary --env-file .env websummary-app
```

3. Access the application at `http://localhost:5001`
http://127.0.0.1:5000/

### Useful Docker Commands

View container logs:
```bash
docker logs $(docker ps -q --filter ancestor=websummary-app)
```

Stop the container:
```bash
docker stop $(docker ps -q --filter ancestor=websummary-app)
```

### Environment Variables
Make sure to set up your environment variables either in a `.env` file or pass them directly:
- OPENAI_API_KEY: Your OpenAI API key without double quotes