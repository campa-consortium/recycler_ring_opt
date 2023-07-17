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

skipthese = ['MPS100AU', 'MPS104BU', 'MPS106AU', 'MPS106BU', 'MPS108AU', 'MPS216BU', 'MPS218AU', 'MPS218BU', 'MPS220AU', 'MPS224AU', 'MPS224BU', 'MPS226AU', 'MPS226BU',
             'MPS230AU', 'MPS230BU', 'MPS232AU', 'MPS232BU', 'MPS310AU', 'MPS310BU', 'MPS312AU', 'MPS312BU', 'MPS316AU', 'MPS316BU', 'MPS318AU', 'MPS318BU', 'MPS322BU',
             'MPS324AU', 'MPS324BU', 'MPS326AU', 'MPS338BU', 'MPS340AU', 'MPS340BU', 'MPS400AU', 'MPS404BU', 'MPS406AU', 'MPS406BU', 'MPS408AU', 'MPS516BU', 'MPS518AU',
             'MPS518BU', 'MPS520AU', 'MPS524AU', 'MPS524BU', 'MPS526AU', 'MPS526BU', 'MPS530AU', 'MPS530BU', 'MPS532AU', 'MPS532BU', 'MPS610AU', 'MPS610BU', 'MPS612AU',
             'MPS612BU', 'MPS616AU', 'MPS616BU', 'MPS618AU', 'MPS618BU', 'MPS622BU', 'MPS624AU', 'MPS624BU', 'MPS626AU', 'MPS638BU', 'MPS640AU', 'MPS640BU',
             'MPS105AU', 'MPS105BU', 'MPS107AU', 'MPS107BU', 'MPS215AU', 'MPS217AU', 'MPS217BU', 'MPS219AU', 'MPS219BU', 'MPS223BU', 'MPS225AU', 'MPS225BU', 'MPS227AU',
             'MPS229BU', 'MPS231AU', 'MPS231BU', 'MPS301AU', 'MPS309BU', 'MPS311AU', 'MPS311BU', 'MPS313AU', 'MPS315BU', 'MPS317AU', 'MPS317BU', 'MPS319AU', 'MPS323AU',
             'MPS323BU', 'MPS325AU', 'MPS325BU', 'MPS327BU', 'MPS339AU', 'MPS339BU', 'MPS341AU', 'MPS341BU', 'MPS405AU', 'MPS405BU', 'MPS407AU', 'MPS407BU', 'MPS517AU',
             'MPS517BU', 'MPS519AU', 'MPS519BU', 'MPS523BU', 'MPS525AU', 'MPS525BU', 'MPS527AU', 'MPS529BU', 'MPS531AU', 'MPS531BU', 'MPS601AU', 'MPS609BU', 'MPS611AU',
             'MPS611BU', 'MPS613AU', 'MPS615BU', 'MPS617AU', 'MPS617BU', 'MPS619AU', 'MPS623AU', 'MPS623BU', 'MPS625AU', 'MPS625BU', 'MPS639AU', 'MPS639BU', 'MPS641AU',
             'MPS641BU']

intmoms = ['K0L', 'K1L', 'K2L', 'K3L']
initial_vals = {'K0LEVEN':  0.0         , 'K0L_ODD':  0.0          ,
                'K1LEVEN':  0.0112332575, 'K1L_ODD': -0.00024562271,
                'K2LEVEN': -0.0050223296, 'K2L_ODD': -0.0331316105 ,
                'K3LEVEN':  0.1297873   , 'K3L_ODD': -0.2137673    }

if __name__ == "__main__":
    # read arguments
    args = parser.parse_args()
    infilename  = args.LatticeFileIn
    outfilename = args.outfilename
    debug       = args.debug

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
    # but for our elements of interest, fill in our tokens for the values of their integrated moments.
    # Additionally, on the first line after the opening "!..." comment lines, introduce our tokens as values.
    lastlinewascomment = True 
    with open(outfilename, 'w') as outfile:
        elements_of_interest = []
        element_name_lengths = []
        for jline in joinedlines:
            # Immediately after the comments, add the lines setting the values of our initial values.
            if lastlinewascomment:
                # Determine whether this line, too, is a comment line
                thislineisacomment = False
                if jline[0] == '!': thislineisacomment = True

                # If the previous line was the final comment line, 
                if thislineisacomment == False :
                    for intmomkey, intmomval in initial_vals.items():
                        outfile.write(f'VALUEFOR_{intmomkey} := {intmomval}\n')
                # Set for next loop around.
                if thislineisacomment: lastlinewascomment = True
                else: lastlinewascomment = False
            # end if lastlinewascomment
                
            if len(jline) < 3:
                outfile.write(jline+'\n')
                continue
            # Is this line just a variable-value assignment, something we can skip?
            if jline.count(':=')>0:
                outfile.write(jline+'\n')
                continue

            # Split the line on spaces, and the first one is where the MPS*U element name might be.
            jparts = jline.split(' ')
            primero = jparts[0]

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

            # Skip the nonphysical upstream multipole shims, wwhich are the 64 even + 66 odd ones in skipthese:
            primero_no_colon = primero[:-1]
            if primero_no_colon in skipthese:
                outfile.write(jline+'\n')
                if debug: print (f'Nonphysical: {jline}')
                continue

            # Keep a list of the primeros, and their lengths. If multiple name lengths are present, the assumptions above are in question!
            elements_of_interest.append(primero)
            element_name_lengths.append(len(primero))
            parity_token = 'EVEN'
            if parity > 0: parity_token = '_ODD'
            
            # Loop the parts of this line, replacing the value with an appropriate token
            newparts = []
            # How to catch and address the cases where certain moments are not in the original file
            for jpart in jparts:
                if jpart[:3] in intmoms: continue # We will replace these with tokens, even if not present in original file.
                newparts.append(jpart)
            # Ensure a final comma, to preceed our list of integrated moments
            final_comma = list(newparts[-1])[-1]
            if not final_comma == ',': newparts[-1] = newparts[-1]+'%'
            for i, intmom in enumerate(intmoms):
                token = 'VALUEFOR_'+intmom+parity_token
            
                if i+1 < len(intmoms): token+= ','
                newparts.append(intmom+'='+token)
            newline = ' '.join(newparts)
            outfile.write(newline+'\n')
        
    if debug: print (f'Elements of interest: {len(elements_of_interest)}')
    if debug: print (f'  and their name lengths: {Counter(sorted(element_name_lengths))}') 
            

        
