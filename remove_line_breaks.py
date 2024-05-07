import argparse
import glob
import os
import time
import re
from collections import Counter

# parse arguments
parser = argparse.ArgumentParser(
    description='Create a template lattice file without MAD-style linebreaks')
parser.add_argument("LatticeFileIn", help="Required input file path")
parser.add_argument('-v','--debug', action='store_true', dest='debug', default=False,
                    help='Verbose debugging output. (default:False)')
parser.add_argument("--outfilename", dest="outfilename", default='',
                    help='Output file name. (default= )')

# global variables
_CURR_DIR = os.path.dirname(os.path.abspath(__file__))


if __name__ == "__main__":
    # read arguments
    args = parser.parse_args()
    infilename  = args.LatticeFileIn
    outfilename = args.outfilename
    debug       = args.debug
    if outfilename == '': outfilename = infilename+'_NoBreaks'
    
    # Undo line wrapping first.
    # MAD-file line wraps may be indicated by a final '&'.
    # Undo all of these, forming a new list of operationally single-line strings.
    joinedlines = []
    with open(infilename,'r') as flatfile:
        print (f'Reading input file {infilename} to make output template file {outfilename}')
        lines = flatfile.readlines()
        if debug: print (f'Read {len(lines)} lines.')
        prevline = ''
        for line in lines:
            thisline = line.strip()
            if len(thisline)<1: continue
            
            # If the line continues past this line (ends with &), just concat this line to the running history
            if thisline[-1]=='&':
                prevline = prevline+thisline[:-1]
                continue
            # Otherwise, we've got a whole, joined line now
            joinedline = prevline+thisline
            prevline = '' # Reset for next line, 
            joinedlines.append(joinedline) # ...and append to the list of whole lines.
    if debug: print(f'len(joinedlines): {len(joinedlines)}.')

    # OK, hold open the outputfile,
    # and dump our joined (unwrapped) lines into it,
    lastlinewascomment = True 
    with open(outfilename, 'w') as outfile:
        for jline in joinedlines:
            outfile.write(jline+'\n')
