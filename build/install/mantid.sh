#!/bin/sh

# Test sudo
$(sudo -n echo)
exitCode=$?
if [ $exitCode -ne 0 ] ; then
    echo "This script must be run with sudo" >&2
    exit 1
fi

set -e

# add the signing key
wget -O - http://apt.isis.rl.ac.uk/2E10C193726B7213.asc -q | sudo apt-key add -

# Add GPG key and upstream Mantid repo
sudo apt-add-repository "deb [arch=amd64] http://apt.isis.rl.ac.uk $(lsb_release -c | cut -f 2) main" -y
sudo apt-add-repository ppa:mantid/mantid -y

sudo apt-get update
sudo apt-get install mantid -y
