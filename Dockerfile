FROM ubuntu:14.04

MAINTAINER niall.robinson@informaticslab.co.uk



RUN apt-get update
RUN apt-get install -y python-pip

RUN apt-get update && apt-get install -y wget bzip2 ca-certificates \
    libglib2.0-0 libxext6 libsm6 libxrender1
RUN echo 'export PATH=/opt/conda/bin:$PATH' > /etc/profile.d/conda.sh && \
    wget --quiet https://repo.continuum.io/miniconda/Miniconda-3.9.1-Linux-x86_64.sh && \
    /bin/bash /Miniconda-3.9.1-Linux-x86_64.sh -b -p /opt/conda && \
    rm Miniconda-3.9.1-Linux-x86_64.sh && \
    /opt/conda/bin/conda install --yes conda==3.14.0

ENV PATH /opt/conda/bin:$PATH

RUN conda install -c scitools iris

ADD [^.]* ./

RUN pip install --upgrade pip
RUN pip install -r requirements.txt