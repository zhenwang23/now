docker build -t now-frontend .

docker tag now-frontend jinaaitmp/now-frontend:0.0.1
docker push jinaaitmp/now-frontend:0.0.1

#docker run -it --rm \
#--name jina-now-frontend \
#-p 80:80 \
#now-frontend