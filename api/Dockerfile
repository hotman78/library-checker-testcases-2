FROM ubuntu:latest

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git g++ python3 python3-pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip

RUN pip3 install colorlog Flask
RUN git clone https://github.com/yosupo06/library-checker-problems.git

RUN ulimit -s unlimited
COPY app.py library-checker-problems/app.py

WORKDIR library-checker-problems
CMD [ "python3", "app.py" ]
EXPOSE 8000