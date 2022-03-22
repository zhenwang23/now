
if [[ $1 == 'darwin' ]]
then
  curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.12.0/kind-darwin-amd64
  chmod +x ./kind
  mkdir -p ~/.cache/jina-now
  mv ./kind ~/.cache/jina-now/kind
fi

if [[ $1 == 'linux' ]]
then
  curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.12.0/kind-linux-amd64
  chmod +x ./kind
  mkdir -p ~/.cache/jina-now
  mv ./kind ~/.cache/jina-now/kind
fi