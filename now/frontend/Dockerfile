FROM jinaai/jina:3.2.8-py37-standard

RUN apt-get update
RUN apt-get -y install

COPY requirements.txt /requirements.txt
RUN pip3 install -r requirements.txt
COPY . /

ENTRYPOINT ["streamlit", "run", "frontend.py", "--server.port", "80", "<node_url>", "31080", "<data>"]