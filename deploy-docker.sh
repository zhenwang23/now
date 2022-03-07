docker build -t jina-now .

docker tag jina-now gcr.io/jina-showcase/vision
docker push gcr.io/jina-showcase/vision

docker tag jina-now jinaaitmp/vision
docker push jinaaitmp/vision

