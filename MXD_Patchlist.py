# Python 2.7 script - constructs a "patchlist" .txt report of broken links within a folder of .mxds; each link coupled with a suggested update path.
# Operates on single directory (non-recursive) of .mxds. Enter directory path under "Variables," or when prompted. The patchlist.txt will also be generated here.
# If only broken links are desired (no suggested update path), set "searchYN" to "'N'"

# Search function caveats:
# Currently does not suggest update paths for broken links that contain generic ESRI "Export_Output" or "Default" keyword.
# Only suggests update paths with the same file or end-folder name as original broken source.
# Search directory IS recursive. i.e. entering "C:\" as searchdir will walk entire C-drive (not recommended).
# Where multiple matching files/end-folders are found, patchlist reports the most recently modified (this isn't always the desired update path!)


## Modules
import arcpy, os, glob, scandir
from scandir import walk
from codecs import open

def main():

    ## Variables
    path = raw_input('Path to folder of .mxds to inspect (non-recursive): \nPatchlist.txt will also be created here') #folder of .mxds to inspect for broken links (non-recursive)
    patchlist = 'patchlist.txt' #name of the patchlist report to create (will overwrite if already exists)
    searchYN = raw_input('Search a directory for updated link locations? (Y/N): \nIf \'N\', patchlist.txt will contain a list of broken links only') #set as 'Y' to search through searchdir for potential update path and list beside broken link, or 'N' to report broken links only
    if searchYN == 'Y' or searchYN == 'y':
        searchdir = raw_input('Path to folder to search through for link updates (recursive):') #folder to search through for link updates (recursive)
    else:
        searchdir = None

    ## Functions
    def find_all(filename, searchdir):
        result = []
        if '.gdb' in filename or '.mdb' in filename:
            for root, dirs, files in scandir.walk(searchdir):
                if filename in dirs:
                    result.append(os.path.join(root, filename))
        elif '.' in filename:
            for root, dirs, files in scandir.walk(searchdir):
                if filename in files:
                    result.append(os.path.join(root, filename))
        else:
            for root, dirs, files in scandir.walk(searchdir):
                if filename in dirs:
                    result.append(os.path.join(root, filename))
        return result

    ## Body
    os.chdir(path) #go to .mxd folder
    mxdlist = glob.glob(os.path.join(path, '*.mxd'))
    reportbroken = set([])

    with open (patchlist, 'w') as patchy:

        for filename in mxdlist:
            try:
                mxd = arcpy.mapping.MapDocument(filename)
                print('\nInspecting ' + filename)
                setbroken = set(arcpy.mapping.ListBrokenDataSources(mxd))

                if len(setbroken) == 0: #skipping files without broken links
                    del mxd #clears variable and releases .mxd
                    print('...\n' +
                          'No broken links found in ' + filename + '\n' +
                          'Skipping file.\n')
                    continue

                for broken in setbroken:
                    if 'Export_Output' in broken.dataSource or 'Default' in broken.dataSource: #skipping broken links with generic keywords
                        continue
                    elif '.xlsx' in broken.dataSource: #handler for .xlsx
                        reportbroken.add(broken.dataSource[0:broken.dataSource.rfind('.') + 5] + ", ")
                    elif '.xls' in broken.dataSource: #handler for .xls
                        reportbroken.add(broken.dataSource[0:broken.dataSource.rfind('.') + 4] + ", ")
                    elif '.gdb' in broken.dataSource or '.mdb' in broken.dataSource: #handler for .gdb and .mdb
                        reportbroken.add(broken.dataSource[0:broken.dataSource.rfind('.') + 4] + ", ")
                    else:
                        reportbroken.add(broken.dataSource + ", ")

            except BaseException as info:
                del mxd #clears variable and releases .mxd
                print('...\n' +
                      'Problem with ' + filename + '\n' +
                      'Info: '),
                print(info)
                print('Skipping file.\n')
                continue

            del mxd #clears variable and releases .mxd

        if searchYN == 'Y' or searchYN == 'y':
            print('There are ' + str(len(reportbroken)) + ' broken links that reqire updates in ' + str(path) + '\n'
                  'Searching ' + str(searchdir) + ' for updated file links...\n' +
                  '(This could take a while)')

            success =0
            for p in reportbroken:
                try:

                    #search for updates
                    print("\nSearching for"),
                    print(p[p.rfind('\\') + 1:-2])
                    searchres = find_all(p[p.rfind('\\') + 1:-2], searchdir)
                    if len(searchres) == 0:
                        print('No updates found for broken link: ' + str(p).replace(', ', '') + '\n' +
                              'Searching for next update...')
                        continue
                    elif len(searchres) == 1: #update found
                        print('1 update found for broken link: ' + str(p).replace(', ', ''))
                        p += str(searchres[0])
                        patchy.write(str(p) + '\n')
                        success += 1
                        print('Added line to patchlist\n' +
                              'Searching for next update...')
                    elif len(searchres) >1: #if multiple updates found
                        print('Multiple updates found for broken link: ' + str(p).replace(', ', ''))
                        temp = []
                        for r in searchres:
                            temp.append(os.path.getmtime(r))
                        p += str(searchres[temp.index(max(temp))])
                        patchy.write(str(p) + '\n')
                        success += 1
                        print('Added line to patchlist (most recently modified)\n' +
                              'Searching for next update...')
                    else:
                        print('Error: unexpected case for broken link: ' + str(p).replace(', ', '') + '\n' +
                              'Searching for next update...')
                        continue

                except BaseException as info:
                    print('...\n' +
                          'Error encountered during search\n' +
                          'Info: '),
                    print(info)
                    print('Searching for next update...')
                    continue

            print('\nAll done\n' +
                  'Found replacements for ' + str(success) + ' of ' + str(len(reportbroken)) + ' broken links\n' +
                  'See ' + str(patchlist) + ' for output')

        elif searchYN == 'N' or searchYN == 'n':
            for p in reportbroken:
                patchy.write(str(p).rstrip(', ') + '\n')
            print('\nAll done\n' +
                  'See ' + str(patchlist) + ' for output')

        else:
            print('Error: searchYN variable must be set to either \'Y\' or \'N\'')

if __name__ == '__main__':
    main()
