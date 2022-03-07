docker build -t jina-now .

docker tag jina-now gcr.io/jina-showcase/now
docker push gcr.io/jina-showcase/now

docker tag jina-now jinaaitmp/now
docker push jinaaitmp/now

