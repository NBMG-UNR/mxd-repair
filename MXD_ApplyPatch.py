# Python 2.7 script - patches over broken links in .mxd files with a user-provided patchlist.
# Operates on single directory (non-recursive). Enter directory path under "Variables".
# This script will overwrite original .mxds; backups strongly recommended.

# Provide patchlist as .txt file in the following format, when prompted:

# -------------------------------------------------------------------------------------
# Path\to\original\brokensource\fileorfolder_1, Path\to\new\repairsource\fileorfolder_1
# Path\to\original\brokensource\fileorfolder_2, Path\to\new\repairsource\fileorfolder_2
# Path\to\original\brokensource\fileorfolder_3, Path\to\new\repairsource\fileorfolder_3
# ...
# Path\to\original\brokensource\fileorfolder_n, Path\to\new\repairsource\fileorfolder_n
# -------------------------------------------------------------------------------------
# Include commas and newlines.
# If filepath contains a geodatabase, point to containing .gdb or .mdb rather than enclosed files.
# If excel sheet, point to containing workbook file.
# See MXD_Patchlist.py for automation (recommended).

# Caveats:
# If corrupted .mxd is encountered, script will fail with "Visual C++ abnormal termination"


## Modules
import arcpy, os, glob
from arcpy import env
from tqdm import tqdm #optional: tqdm is simply an ETA/progress monitor. if not using, remove funtion @ line 119

def main():

    ## Variables
    path = raw_input('Path to folder of .mxds to repair: ') #folder of .mxds to repair (non-recursive)
    patchlist = raw_input('Path to .txt patchlist file (see readme for patchlist format): ') #path to .txt file containing patchlist (see readme for patchlist format)

    ## Setup
    print('Setting environment paths...')
    mxdlist = glob.glob(os.path.join(path, '*.mxd'))
    env.workspace = path
    arcpy.env.scratchWorkspace = path
    env.overwriteOutput = True
    arcpy.gp.overwriteOutput = True
    print('Paths set.')

    ## Body
    with open (patchlist, 'rt') as patchy:

        attempt = 0
        success = 0
        patch = [line.rstrip('\n') for line in patchy] #list of full lines in patchlist
        patchy.seek(0)
        source = [line[0:line.rfind(',')] for line in patchy]  #list of broken links in patchlist
        patchy.seek(0)
        repair = [line[line.rfind(',') + 2:-1] for line in patchy] #list of repair links in patchlist

        for filename in mxdlist:

            haystack = [] #initialize list of find arguments for find/replace (per entire patchlist)
            needles = set([]) #initialize set find arguments (per individual .mxd file)
            update = []

            try:
                mxd = arcpy.mapping.MapDocument(filename)
                print('\nProcessing ' + filename)

                listbroken = arcpy.mapping.ListBrokenDataSources(mxd)

                if len(listbroken) == 0: #skipping files without broken links
                    attempt += 1
                    patchy.seek(0)
                    del mxd #clears variable and releases .mxd
                    del haystack, needles, update
                    print('...\n' +
                          'No broken links found in ' + filename + '\n' +
                          'Skipping file...\n')
                    continue

                # format broken paths (from patchlist) for findAndReplaceWorkspacePaths
                for h in source:
                    if any(db in h for db in ['.gdb', '.mdb']) or '.' not in h: #handler for .gdb, .mdb, and directories
                        haystack.append(h)
                    else: #handler for files
                        haystack.append(h[0:h.rfind('\\')])

                # format repair paths (from patchlist) for findAndReplaceWorkspacePaths
                for up in repair:
                    if any(db in up for db in ['.gdb', '.mdb']) or '.' not in up: #handler for .gdb, .mdb, and directories
                        update.append(up)
                    else: #handler for files
                        update.append(up[0:up.rfind('\\')])

                # format set of broken links (from mxd inspection) to check against patchlist
                for broken in listbroken:
                    if any(db in broken.dataSource for db in ['.gdb', '.mdb']): #handler for .gdb and .mdb
                        needles.add(broken.dataSource[0:broken.dataSource.rfind('.') + 4])
                    elif '.xls' in broken.dataSource: #handler for .xls(x) sheets
                        needles.add(broken.dataSource[0:broken.dataSource.rfind('\\', 0, broken.dataSource.rfind('.'))])
                    elif '.' in h: #handler for other files
                        needles.add(broken.dataSource[0:broken.dataSource.rfind('\\')])
                    else: #other directories
                        needles.add(broken.dataSource)

                # flag indices of broken links occuring in the patchlist (as to not force the entire patchlist on each .mxd)
                index = [idx for idx, val in enumerate(haystack) if val in needles]

                # skip files with no suitible patch lines
                if len(index) == 0:
                    attempt += 1
                    patchy.seek(0)
                    del mxd #clears variable and releases .mxd
                    del haystack, needles, update
                    print('...\n' +
                          'No updates in patchlist apply to ' + filename + '\n' +
                          'Skipping file...\n')
                    continue

                # make patch for current .mxd (brokensource-repair tuples formatted for findAndReplaceWorkspacePaths)
                filepatch = []
                for i in index:
                    filepatch.append(haystack[i] + ', ' + update[i])

                # repair broken links
                for tupl in tqdm(filepatch): #tqdm is simply an ETA/progress monitor. drop function if not using module
                    link = tupl.split(", ")
                    mxd.findAndReplaceWorkspacePaths(link[0], link[1])

                # save mxd (overwrite)
                mxd.save() #overwrites .mxd with patched version
                attempt += 1
                success += 1
                patchy.seek(0)
                del mxd #clears variable and releases .mxd
                del haystack, needles, update
                print('\nFinished processing ' + filename + '\n' +
                      'Loading next file...\n')

            except BaseException as info:
                attempt += 1
                patchy.seek(0)
                del mxd #clears variable and releases .mxd
                del haystack, needles, update
                print('...\n' +
                      'Problem with ' + filename + '\n' +
                      'Info: '),
                print(info)
                print('Skipping file...\n')
                continue

    print('\nAll done\n' +
          str(attempt) + ' files attempted\n' +
          str(success) + ' files successfully patched')

if __name__ == '__main__':
    main()
