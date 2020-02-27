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
# Note this will install the nightly and should be changed once 4.3 is released.
sudo apt-add-repository "deb [arch=amd64] http://apt.isis.rl.ac.uk $(lsb_release -c | cut -f 2)-testing main" -y
sudo apt-add-repository ppa:mantid/mantid -y

sudo apt-get update
sudo apt-get install mantidnightly-python3 -y

export PYTHONPATH=$PYTHONPATH:/opt/mantidnightly-python3/lib:/opt/mantidnightly-python3/bin

# Run simpleapi as this can cause segfaults if not allowed to finish
# Use mantidpython (not python) as mantidpython waits for completion whereas python exits while still downloading
/opt/mantidnightly-python3/bin/mantidpython -m  mantid.simpleapi

echo "Mantid is now setup for this session."
echo "To enable mantid in future sessions we recommend adding 'export PYTHONPATH=\$PYTHONPATH:/opt/mantidnightly-python3/lib;/opt/mantidnightly-python3/bin' to your .bashrc file"
