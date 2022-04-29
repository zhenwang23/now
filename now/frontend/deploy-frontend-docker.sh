docker build -t now-frontend .

docker tag now-frontend jinaai/now-frontend:0.0.4
docker push jinaai/now-frontend:0.0.4

#docker run -it --rm \
#--name jina-now-frontend \
#-p 80:80 \
#now-frontend