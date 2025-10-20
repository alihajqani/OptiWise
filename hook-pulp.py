# File: hook-pulp.py
# This script runs right after PyInstaller extracts all bundled files.
# Its sole purpose is to find the 'cbc' solver executable within the
# temporary directory and set its execute permission, which is a common
# issue when bundling applications on Linux.

import sys
import os
import stat

# This code should only run on Linux systems.
if sys.platform.startswith('linux'):
    
    # The 'frozen' attribute is set to True by PyInstaller when running the bundled app.
    # The _MEIPASS attribute holds the path to the temporary extraction folder.
    if hasattr(sys, '_MEIPASS'):
        
        # Construct the expected path to the cbc executable inside the temp folder.
        # This path must match the internal structure of the 'pulp' package.
        cbc_path = os.path.join(sys._MEIPASS, 'pulp', 'solverdir', 'cbc', 'linux', 'l64', 'cbc')

        # First, check if the file actually exists at that path before proceeding.
        if os.path.exists(cbc_path):
            print(f"[hook-pulp.py] Found CBC solver at: {cbc_path}")
            
            # Get the current permission bits of the file.
            current_permissions = stat.S_IMODE(os.stat(cbc_path).st_mode)
            
            # Define the execute permission bits for user, group, and others.
            execute_permissions = stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
            
            # Combine the current permissions with the execute permissions using a bitwise OR.
            new_permissions = current_permissions | execute_permissions
            
            # Apply the new, executable permissions to the file.
            os.chmod(cbc_path, new_permissions)
            
            print(f"[hook-pulp.py] Successfully set execute permissions for CBC solver.")
        else:
            # This message will appear in the console if the file wasn't bundled correctly.
            print(f"[hook-pulp.py] ERROR: CBC solver not found at expected path: {cbc_path}")