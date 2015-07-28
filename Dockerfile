FROM niallrobinson/iris

MAINTAINER niall.robinson@informaticslab.co.uk

ADD [^.]* ./

RUN pip install --upgrade pip
RUN pip install -r requirements.txt