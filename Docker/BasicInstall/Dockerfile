# Use ubuntu as a parent image
FROM ubuntu:18.04

# Install the packages we need to build fitbenchmarking
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    python3-venv \
    git

# set up a venv to stop python/python3 sillyness
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip install pytest>3.6 \
    		pytest-cov \
		coveralls \
		python-coveralls \
		urllib3==1.23 \
                mock
		
WORKDIR /home/
    


