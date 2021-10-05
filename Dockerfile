FROM ubuntu:16.04
WORKDIR /home/vis
COPY . .
RUN apt-get update
RUN apt-get install -y python3-pandas
RUN apt-get install -y python3-pip
RUN pip3 install music21==2.1.2
RUN pip3 install requests==2.11.1
RUN pip3 install multi-key-dict==2.0.3
RUN python3 setup.py install
CMD ["bash"]
