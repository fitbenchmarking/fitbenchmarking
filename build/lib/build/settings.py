"""
Settings for install directories
"""
import os

if os.name == 'nt':
    # WINDOWS SETTINGS
    INSTALL_DIRS = {
        'mantid': 'C:\\fitbenchmarking_deps\\mantid\\',
        '7zip': 'C:\\fitbenchmarking_deps\\7zip\\',
        '7zip-location': 'C:\\Program Files\\7-Zip',
    }
else:
    # LINUX SETTINGS
    INSTALL_DIRS = {
        'mantid': '/opt/Mantid'
    }
    # 7Zip not required on linux
