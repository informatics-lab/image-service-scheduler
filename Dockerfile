FROM quay.io/informaticslab/iris
MAINTAINER niall.robinson@informaticslab.co.uk

# Install system dependancies
RUN apt-get update && apt-get install -y git

# Pull in service configuration
RUN git clone https://github.com/met-office-lab/cloud-processing-config.git config

# Install service dependancies
ADD requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Add code
ADD scheduler.py scheduler.py

# Run code
CMD ./scheduler.py
