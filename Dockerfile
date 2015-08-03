FROM quay.io/informaticslab/iris
MAINTAINER niall.robinson@informaticslab.co.uk

RUN apt-get update && apt-get install -y git

RUN git clone https://github.com/met-office-lab/cloud-processing-config.git config 

ADD requirements.txt requirements.txt
ADD scheduler.py scheduler.py

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ./scheduler.py