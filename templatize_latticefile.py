import argparse
import glob
import os
import time
from collections import Counter

# parse arguments
parser = argparse.ArgumentParser(
    description='Create a template lattice file with placeholders.')
parser.add_argument("LatticeFileIn", help="Required input file path")
parser.add_argument('-v','--debug', action='store_true', dest='debug', default=False,
                   help='Verbose debugging output. (default:False)')
parser.add_argument("--outfilename", dest="outfilename", default='RR2020V0922_TEMPLATE_fixed',
                    help='Output file name. (default= RR2020V0922_TEMPLATE_fixed)')
parser.add_argument("--element-regex", dest='element_regex', default='MPS*U',
                    help='String pattern to match. (default: "MPS*U")')
parser.add_argument('--split-by-parity', dest='split_by_parity', default=True,
                    help='Split elements even/odd. (default: True)')
# global variables
_CURR_DIR = os.path.dirname(os.path.abspath(__file__))

intmoms = ['K1L', 'K2L', 'K3L', 'K4L']
if __name__ == "__main__":
    # read arguments
    args = parser.parse_args()
    infilename  = args.LatticeFileIn
    outfilename = args.outfilename
    debug       = args.debug

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

    with open(outfilename, 'w') as outfile:
        elements_of_interest = []
        element_name_lengths = []
        for jline in joinedlines:
            if len(jline) < 8:
                outfile.write(jline+'\n')
                continue
            # Is this line just a veriable-value assignment, something we can skip?
            if jline.count(':=')>0:
                outfile.write(jline+'\n')
                continue
        
            lineparts = jline.split(' ')
            primero = lineparts[0]
            # Skip lines that don't define a lattice element, which are always declared as "ELEMENTNAME: ...etc..."
            if not primero[-1] == ':':
                outfile.write(jline+'\n')
                continue
            # Elements which begin "MPS" and end "U:" only, please.
            if not (primero[:3] == 'MPS' and primero[-2]=='U'):
                outfile.write(jline+'\n')
                continue
            
            # Extract the element number to handle even and odd elements separately
            elem_digits = primero[3:6]
            parity = int(elem_digits)%2
            
            elements_of_interest.append(primero)
            element_name_lengths.append(len(primero))
            parity_token = 'EVEN'
            if parity > 0: parity_token = '_ODD'
            
            # Loop the parts of this line, replacing the value with an appropriate token
            jparts = jline.split(' ')
            newparts = []
            # How to catch and address the cases where certain moments are not in the original file
            for jpart in jparts:
                if jpart[:3] in intmoms: continue # We will replace these with tokens, even if not present in original file.
                newparts.append(jpart)
            # Ensure a final comma, to preceed our list of integrated moments
            final_comma = list(newparts[-1])[-1]
            if not final_comma == ',': newparts[-1] = newparts[-1]+'%'
            for i, intmom in enumerate(intmoms):
                token = 'REPLACEME_'+intmom+parity_token
            
                if i+1 < len(intmoms): token+= ','
                newparts.append(intmom+'='+token)
            newline = ' '.join(newparts)
            outfile.write(newline+'\n')
        
    if debug: print (f'Elements of interest: {len(elements_of_interest)}')
    if debug: print (f'  and their name lengths: {Counter(sorted(element_name_lengths))}') 
            

        
