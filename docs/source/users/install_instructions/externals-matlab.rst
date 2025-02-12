.. _external-instructions-matlab:

####################################################
Installing Matlab through WSL in a Linux environment
####################################################

There are a couple of different ways to install MATLAB through WSL in a Linux environment, one of which requires X11 Forwarding, 
while the other doesn't require a graphical interface.


.. _with_x11_forwarding:

Method 1: through X11 Forwarding
********************************

X11 Forwarding can be enabled through a server like VcXsrv, an X server for Windows, which allows users to run graphical apps 
from a Linux environment on a Windows  machine. 

Enabling X11 Forwarding
-----------------------

Given VcXsrv has been installed, the following steps are necessary to enable it:

#. Start XLaunch.
#. Click "Next" till the window "Extra settings".
#. In the window "Extra settings", make sure the last box is ticked. 
#. Click "Next" and then "Finish".

For X11 Forwarding to work, It is also necessary to set a couple of environment variables, if these have no value.
* The environment variable called ``DISPLAY`` needs to have a value. If it doesn't, it can be set by running, e.g., ``export DISPLAY=:0`` 
   (this could be added to `~./bashrc`). 
* The environment variable ``LIBGL_ALWAYS_INDIRECT`` must be set to 1.

At this point, X11 Forwarding can be tested by running ``xeyes`` from the WSL Linux environment, which should cause a pop-up with a 
pair of eyes to appear. If ``xeyes`` does not work at this point, one should do the following:

#. Check the inbound rules for VcXsrv, by navigating to Control Panel > System and Security > Defender Firewall > Advanced settings > Inbound rules. 
#. Here, there should be two rules with the name "VcXsrv windows server" marked as Public. If these have red stop signs next to them, 
   click on them and "allow" the connection. This operation requires admin rights. 

Once this has been done, running ``xeyes`` should work and open the pop-up. 

Having configured the X11 Forwarding, this can be used for installing MATLAB. For this, one should follow the instructions 
in `<https://uk.mathworks.com/help/install/ug/install-products-with-internet-connection.html>`_, making sure that the 
version of MATLAB being downloaded is compatible with the Python version being used. The following page might help with 
that: `<https://uk.mathworks.com/support/requirements/python-compatibility.html>`_. 

After running ``sudo ./install`` from the MATLAB folder (as suggested in the Mathworks instructions), the graphical interface 
will open. Here, the user is asked to select a suitable folder for the MATLAB installation. Let's call this path `<matlabroot>`. 
In the last window, before the installation starts, there should be a question on whether to create symbolic links and where. 
That box should be ticked, and the path provided there should correspond to the previously selected `<matlabroot>`.

Finally, the path `<matlabroot>/bin/glnxa64` should be added to ``LD_LIBRARY_PATH``, and the path `<matlabroot>/bin` should be 
added to both ``PATH`` and ``PYTHONPATH``.


.. _without_graphical_interface:

Method 2: without graphical interface
*************************************

The following instructions allow to install Matlab without using X11 Forwarding.

Get the software
----------------

#. Download the installer in Windows from Matlab: `<https://uk.mathworks.com/downloads/>`_. 
#. Log in to your mathworks account.
#. Go to "Advanced Options" in the installer and select "Download without installing".
#. Select the toolboxes you want to install.
#. Copy the download to WSL.


.. _get-mac-address:

Get the current mac address
---------------------------

#. Open WSl and type ``ip link show bond0``.
#. Note the mac address (just after ``link/ether`` in the output).


Get the licence
---------------

#. Go to the mathworks licence centre (this may require you to log in): `<https://uk.mathworks.com/licensecenter/licenses>`_. 
#. Click on your licence.
#. Go to the "Install and Activate" tab.
#. Click "View current activations" on the right hand menu.
#. Click "Activate a computer".
#. Fill in the form:
  * Operating System: Linux
  * Host ID: `<host-id>`
  * Computer login name: Your username in WSL
  * Activation Label: A unique identifier for the licence (e.g. "R2022b wsl")
  Note that `<host-id>` is the one noted down in :ref:`_get-mac-address`.

#. Download the licence file to WSL and copy the file installation key somewhere temporarily.
#. Create a "prep_matlab" function in one of your `~/.profile`, `~/.bashrc`, `~/.bash_aliases` or whatever you use. This will allow
   you to reset an unused mac address to the one required for the licence.

.. code-block:: rst
    prep_matlab() {
        wantmac=<host-id>
        mac=$(ip link show bond0 | awk '/ether/ {print $2}')
        if [[ $mac !=  $wantmac ]]; then
            sudo ip link set dev bond0 address $wantmac
        fi
    }


Install
-------

#. Unzip the download.
#. Edit the `installer_input.txt` file setting the following:
  * Destination folder (e.g. `destinationFolder=/home/alister/MATLAB/R2022b`).
  * File installation key from the licence steps.
  * Agree to licence (`agreeToLicense=yes`)
  * Output file - if anything fails this is the only way to get information (e.g. `outputFile=/home/alister/temp/mathworks.log`)
  * Improve matlab (e.g. `improveMATLAB=no`)
  * Licence path (e.g. `licensePath=/home/alister/MATLAB/2022_10_17_16_19_39/license.lic`)
  * Uncomment all downloaded packages -- These must be a subset of the ones selected in Get the software, it won't download extras.
#. Run `./install -inputFile installer_input.txt`