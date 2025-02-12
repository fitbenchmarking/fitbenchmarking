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
from a Linux environment on a Windows  machine. Once installed, one needs to start XLaunch, click "Next" till the window 
"Extra settings", where the last box needs to be ticked for VcXsrv to function correctly. X11Forwarding can be tested by 
running ``xeyes`` from the WSL Linux environment, which should cause a pop-up with a pair of eyes to appear. For ``xeyes`` to 
work, the environment variable called ``DISPLAY`` must have a value, which can be set by running, e.g., ``export DISPLAY=:0``. 
This could be added to `~./bashrc` to avoid repeating every time a terminal is started. It might also be necessary to set 
the environment variable ``LIBGL_ALWAYS_INDIRECT`` to 1. If ``xeyes`` does not work at this point, one should check the inbound 
rules for VcXsrv, by navigating to 
Control Panel > System and Security > Defender Firewall > Advanced settings > Inbound rules. Here, there should be 
two rules with the name "VcXsrv windows server" marked as Public. If these have red stop signs next to them, one should
double click on them and "allow" the connection. This operation requires admin rights on the machine. 
Once all this has been done, running ``xeyes`` should work and open the pop-up. 

Having configured the X11 Forwarding, this can be used for installing MATLAB. For this, one should follow the instructions 
in `<https://uk.mathworks.com/help/install/ug/install-products-with-internet-connection.html>`_, making sure that the 
version of MATLAB being downloaded is compatible with the Python version being used. The following page might help with 
that: `<https://uk.mathworks.com/support/requirements/python-compatibility.html>`_. 

After running ``sudo ./install`` from the MATLAB folder (as suggested in the Mathworks instructions), the graphical interface 
will open. Here, the user is asked to select suitable folder for the MATLAB installation. Let's call this path `<matlabroot>`. 
In the last window, before the installation starts, there should be a question on whether to create symbolic links and where. 
That box should be ticked, and the path provided there should correspond to the previously selected `<matlabroot>`.
Finally, the path `<matlabroot>/bin/glnxa64` should be added to ``LD_LIBRARY_PATH``, and the path `<matlabroot>/bin` should be 
added to both ``PATH`` and ``PYTHONPATH``.


.. _without_graphical_interface:

Method 2: without graphical interface
*************************************
