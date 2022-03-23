FROM jinaai/jina:3.2.8-py37-standard

RUN apt-get update && apt-get -y install ca-certificates curl gnupg lsb-release && \
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg && \
    apt-get update && apt-get -y install docker.io && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean

# Install kubectl
RUN curl -LO https://storage.googleapis.com/kubernetes-release/release/v1.17.0/bin/linux/amd64/kubectl && \
    chmod +x ./kubectl && \
    mv ./kubectl /usr/local/bin/kubectl

# Install Kubernetes in Docker (kind)
RUN curl -Lo ./kind https://github.com/kubernetes-sigs/kind/releases/download/v0.11.1/kind-linux-amd64 && \
    chmod +x ./kind && \
    mv ./kind /usr/local/bin/kind

RUN apt-get update && apt-get install -y nano && \
    curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-374.0.0-linux-x86_64.tar.gz && \
    tar -xf google-cloud-sdk-374.0.0-linux-x86_64.tar.gz && rm google-cloud-sdk-374.0.0-linux-x86_64.tar.gz && \
    ./google-cloud-sdk/install.sh -q

COPY requirements.txt /requirements.txt
RUN pip3 install --no-cache -r requirements.txt && \
    rm -rf ~/.local/ &&  rm -rf ~/.cache/
RUN pip3 install yaspin

COPY . /root/
WORKDIR "/root"

ENV PATH="${PATH}:/root"
ENV PATH="${PATH}:/google-cloud-sdk/bin/"
ENV PYTHONUNBUFFERED=1
ENV JINA_LOG_LEVEL=ERROR
ENTRYPOINT ["python3", "-u", "run_all_k8s.py"]