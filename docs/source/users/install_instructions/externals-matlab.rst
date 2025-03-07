.. _external-instructions-matlab:

####################################################
Installing Matlab through WSL in a Linux environment
####################################################

There are a couple of ways to install MATLAB through WSL in a Linux environment, one of which requires X11 Forwarding, 
while the other doesn't require a graphical interface. 

Note that these instructions assume that WSL is running a Ubuntu/Debian based system, and using a bash shell. The user 
should follow the equivalent steps for their setup if it differs.


.. _with_x11_forwarding:

Method 1: through X11 Forwarding
********************************

X11 Forwarding can be enabled through a server like VcXsrv, an X server for Windows that allows users to run graphical apps 
from a Linux environment on a Windows  machine. 

Enabling X11 Forwarding
-----------------------

To check whether X11 Forwarding is already enabled, run ``xeyes`` from the WSL Linux environment. ``xeyes`` can be installed  
through the command ``sudo apt install x11-apps`` and running ``xeyes`` should cause a pop-up with a pair of eyes to appear.

If X11 Forwarding is not already enabled, install VcXsrv on your Windows machine 
(you can find installation instructions at `<https://vcxsrv.com/>`_) and follow these steps to enable it:

#. Start XLaunch.
#. Click "Next" till the window "Extra settings".
#. In the window "Extra settings", make sure the box "Disable access control" is ticked. 
#. Click "Next" and then "Finish".

For X11 Forwarding to work, it is also necessary to set a couple of environment variables (this could be done through `~./bashrc`, 
to make sure there is no need to repeat the process in the future). Specifically, the environment variable called ``DISPLAY`` can be 
set by running, e.g., ``export DISPLAY=:0``, and the environment variable ``LIBGL_ALWAYS_INDIRECT`` must be set to 1.

At this point, X11 Forwarding can be tested again by running ``xeyes``. If ``xeyes`` still does not work, follow these steps:

#. Navigate to Control Panel > System and Security > Defender Firewall > Advanced settings > Inbound rules. 
#. Here, there should be two rules with the name "VcXsrv windows server" marked as Public. If these have red stop signs next to them, 
   click on them and "allow" the connection. This operation requires admin rights. 

Once this has been done, running ``xeyes`` should work and open the pop-up. 


Installing MATLAB
-----------------

Having configured the X11 Forwarding, this can be used for installing MATLAB. For this, one should follow the instructions 
in `<https://uk.mathworks.com/help/install/ug/install-products-with-internet-connection.html>`_. It is possible to check that the 
version of MATLAB being downloaded is compatible with the Python version being used, by referring to 
`<https://uk.mathworks.com/support/requirements/python-compatibility.html>`_. 

If the user finds difficulty downloading the MALTAB Linux version from a Windows machine at the link provided in the MathWorks 
instructions, then the other option would be to do so by using a browser on WSL. 

Assuming the user is able to download the MATLAB installation compressed files on the Windows machine, it will be necessary to copy the  
folder to the WSL environment and unzip it there. On WSL, the user should be able to access their Windows system  at the path 
`/mnt/c/Users/<windows.username>/` and then use the command ``cp`` to copy the compressed folder across to the desired 
location on WSL. We recommend creating a dedicated folder on WSL where to unzip it. Then, the compressed file can be unzipped using 
a command like ``unzip compressed_file.zip -d destination_folder``. The ``unzip`` command can be installed with 
``sudo apt-get install unzip``.

As suggested in the MathWorks instructions, the user should run the install script from the installation folder using sudo. 
Running install using sudo will allow MATLAB to be installed in the default path `/usr/local/`. Once the graphical interface has 
opened, the user is asked the confirm (or change) this path. Let's call this path `<matlabroot>`. 
Next, it will be necessary to select the toolboxes to include in the installation, and the following should be ticked: 
MATLAB, Curve Fitting Toolbox, Optimization Toolbox, and Statistics and Machine Learning Toolbox.
In the last window, before the installation starts, there will be a question on whether to create symbolic links and where. 
Ticking that box is needed if the selected `<matlabroot>` does not correspond to the default `/usr/local/`, and the path 
provided there should correspond to the previously used `<matlabroot>`.


.. _without_graphical_interface:

Method 2: without graphical interface
*************************************

The following instructions allow to install Matlab without using X11 Forwarding.

.. _get-software:

Get the software
----------------

#. Download the installer in Windows from Matlab: `<https://uk.mathworks.com/downloads/>`_. 
#. Log in to your MathWorks account.
#. Go to "Advanced Options" in the installer and select "Download without installing".
#. Select the toolboxes you want to install. We recommend selecting MATLAB, Curve Fitting Toolbox, Optimization Toolbox, and Statistics and Machine Learning Toolbox.
#. Copy the download to WSL.


.. _get-mac-address:

Get the current mac address
---------------------------

#. Open WSL and type ``ip link show bond0``.
#. Note the mac address (just after ``link/ether`` in the output).


Get the licence
---------------

#. Open the MathWorks licence centre (this may require logging in): `<https://uk.mathworks.com/licensecenter/licenses>`_. 
#. Click on the MALTAB licence.
#. Go to the "Install and Activate" tab.
#. Click "View current activations" on the right hand menu.
#. Click "Activate a computer".
#. Fill in the form:

    * Operating System: Linux
    * Host ID: `<host-id>` (the mac address noted in :ref:`get-mac-address`)
    * Computer login name: Username in WSL
    * Activation Label: A unique identifier for the licence (e.g. "R2022b wsl")
    
#. Download the licence file to WSL and copy the file installation key somewhere temporarily.
#. Create a "prep_matlab" function in one of `~/.profile`, `~/.bashrc`, or `~/.bash_aliases`. This will reset an unused mac address to the one required for the licence.

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

Unzip the download and edit the `installer_input.txt` file, setting the following:

    * Destination folder.
    * File installation key from the licence steps.
    * Agree to licence (`agreeToLicense=yes`).
    * Output file - if anything fails this is the only way to get information.
    * Improve matlab (e.g. `improveMATLAB=no`).
    * Licence path.
    * Uncomment all downloaded packages -- these must be a subset of the ones selected in :ref:`get-software`, it will not download extras.

Run `./install -inputFile installer_input.txt`