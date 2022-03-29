docker build -t jina-now .

docker tag jina-now jinaaitmp/now:0.0.1
docker push jinaaitmp/now:0.0.1

