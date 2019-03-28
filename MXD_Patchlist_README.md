### Python 2.7 script - constructs a "patchlist" .txt report of broken links within a folder of .mxds; each link coupled with a suggested update path.
Operates on single directory (non-recursive) of .mxds. Enter directory path under "Variables," or when prompted. The patchlist.txt will also be generated here.
If only broken links are desired (no suggested update path), set "searchYN" to "N"

*Search function caveats:*

Currently does not suggest update paths for broken links that contain generic ESRI "Export_Output" or "Default" keyword.

Only suggests update paths with the same file or end-folder name as original broken source.

Search directory IS recursive. i.e. entering "C:\" as searchdir will walk entire C-drive (not recommended).

Where multiple matching files/end-folders are found, patchlist reports the most recently modified (this isn't always the desired update path!)
