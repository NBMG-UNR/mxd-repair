### Python 2.7 script - patches over broken links in .mxd files with a user-provided patchlist.
Operates on single directory (non-recursive). Enter directory path under "Variables," or when prompted.

This script will overwrite original .mxds; backups strongly recommended.

Provide patchlist as .txt file in the following format, when prompted:

> Path\to\original\brokensource\fileorfolder_1, Path\to\new\repairsource\fileorfolder_1
> Path\to\original\brokensource\fileorfolder_2, Path\to\new\repairsource\fileorfolder_2
> Path\to\original\brokensource\fileorfolder_3, Path\to\new\repairsource\fileorfolder_3

> ...

> Path\to\original\brokensource\fileorfolder_n, Path\to\new\repairsource\fileorfolder_n

Include commas and newlines.
If filepath contains a geodatabase, point to containing .gdb or .mdb rather than enclosed files.
If excel sheet, point to containing workbook file.
See MXD_Patchlist.py for automation (recommended).

*Caveats:*

If corrupted .mxd is encountered, script will fail with "Visual C++ abnormal termination"
