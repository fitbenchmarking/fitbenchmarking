# First, let's setup the basics
apt-get update
apt-get install -y \
	python3 \
	python3-pip \
	python3-dev \
	python3-venv \
	git \
	sudo \
	cmake

export VIRTUAL_ENV=/opt/venv
python3 -m venv $VIRTUAL_ENV
export PATH="$VIRTUAL_ENV/bin:$PATH"

pip install wheel
pip install pytest>3.6 \
            pytest-cov \
	    coveralls \
	    coverage~=4.5.4 \
            urllib3==1.23 \
	    mock
