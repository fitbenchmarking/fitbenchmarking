#################
Installing Mantid
#################


Windows
=======

The fitbenchmarking setup does not currently support installing mantid
through it. Mantid can be downloaded from
`here <http://download.mantidproject.org/>`__. From the `Mantid
installation instructions
page <http://download.mantidproject.org/windows.html>`__:

The steps below will guide you through installation of Mantid on
Windows:

1. Find the version of Mantid you previously downloaded. By default, it
   will automatically download to your downloads folder, which is
   located at: ``C:\Users\$USER\Downloads`` where
   ``$USER`` is your Windows username.
2. Double click the installer and click **Run**.
3. Go through the steps of the installer. The default settings are
   recommended.
4. Once you click **Install** the installation process will begin, and
   inform you when it is complete.
5. That’s it! Once the installation process is complete a MantidPlot
   icon will appear on your desktop, and in your start menu.

**Note**: the installer will look for the drive with the most free disk
space, which may include external devices. Installing and uninstalling
on these devices is extremely slow, and not recommended.

Linux
=====

Installing Through the FitBenchmarking Tool
-------------------------------------------

The fitbenchmarking tool does support installing mantid through it on
Ubuntu 16.04 and Ubuntu 18.04. Open up a terminal and cd into the
fitbenchmarking folder. Here, type ``python setup.py help`` and follow
the instructions there to install mantid or any additional external
software. For clarity, it is as simple as running
``python setup.py externals -s mantid``

Manual Installation - Terminal
------------------------------

If for some reason this does not work for you, a manual installation
might instead. From the `Mantid installation instructions
page <http://download.mantidproject.org/ubuntu.html>`__

   1. Open up a terminal
   2. Run the following commands one line at a time:

::

   # add the mantid signing key
   wget -O - http://apt.isis.rl.ac.uk/2E10C193726B7213.asc | sudo apt-key add -
   sudo apt-add-repository "deb [arch=amd64] http://apt.isis.rl.ac.uk $(lsb_release -c | cut -f 2) main"
   sudo apt-add-repository ppa:mantid/mantid

3. Install the package with

::

   sudo apt-get update
   sudo apt-get install mantid

This will install Mantid into ``/opt/Mantid`` and add bash files to
``/etc/profile.d`` so that next time you create a terminal the correct path
to MantidPlot will be defined.

Manual Installation - Package
-----------------------------

To download the package manually go
`here <http://download.mantidproject.org/>`__. To install a package
manually, first install gdebi: ``sudo apt-get install gdebi`` then
install mantid using: ``sudo gdebi pkgname.deb`` while you are in the
folder from where you downloaded mantid and replace pckgname with the
name of the downloaded file.
