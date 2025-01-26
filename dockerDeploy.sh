docker stop websummary
docker rm websummary
docker build -t websummary-app . 
docker run -p 5001:5000 --name websummary --env-file .env websummary-app
