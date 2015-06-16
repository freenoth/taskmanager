import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = { 'icon' : 'wm.ico',
                      'include_files' : ['wm.ico',
                                         'workmanager.conf',
                                         'workmanager.sublime-project'] }
  # "packages": ["os"], "excludes": ["tkinter"]}

# GUI applications require a different base on Windows (the default is for a
# console application).
# base = None
# if sys.platform == "win32":
base = "Win32GUI"

setup(  name = "WorkManager",
        version = "0.2.1a",
        description = "Work manager lalala",
        options = {"build_exe": build_exe_options},
        executables = [Executable("workmanager.pyw", base=base)])