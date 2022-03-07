docker build -t now-frontend .

docker tag now-frontend gcr.io/jina-showcase/now-frontend
docker push gcr.io/jina-showcase/now-frontend

docker tag now-frontend jinaaitmp/now-frontend
docker push jinaaitmp/now-frontend

#docker run -it --rm \
#--name jina-now-frontend \
#-p 80:80 \
#now-frontend