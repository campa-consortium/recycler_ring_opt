import argparse
import glob
import os
import time
import re
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

intmoms = ['K0L', 'K1L', 'K2L', 'K3L', 'K4L']
initial_vals = {'K0L_EVEN':  0.0         , 'K0L_ODD':  0.0          ,
                'K1L_EVEN':  0.0112332575, 'K1L_ODD': -0.00024562271,
                'K2L_EVEN': -0.0050223296, 'K2L_ODD': -0.0331316105 ,
                'K3L_EVEN':  0.1297873   , 'K3L_ODD': -0.2137673    ,
                'K4L_EVEN':  0.0         , 'K4L_ODD':  0.0          }

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
                    outfile.write("! Set values for the variables to adjust multipole moments\n")
                    for intmomkey, intmomval in initial_vals.items():
                        outfile.write(f'!VALUEFOR_{intmomkey} := 0.0\n')
                # Set for next loop around.
                if thislineisacomment: lastlinewascomment = True
                else: lastlinewascomment = False
            # end if lastlinewascomment
                
            # pass through any very short lines
            if len(jline) < 3:
                outfile.write(jline+'\n')
                continue
            # Is this line just a variable-value assignment, something we can skip?
            if jline.count(':=')>0:
                outfile.write(jline+'\n')
                continue

            # this pattern matches strings like:
            # MPS123AU: blahblay, K1L=plugh, K2L=xyzzy, K3L=fnord
            # the three-digit element number [A or B] text
            #          and values of K1L K2L K3L are captured as
            # \1 \2 \3
            #          \4 \5 \6.
            
            mo = re.match(r"^MPS([1-6]\d\d)([AB])U: (.*), K1L=(.*), .*K2L=(.*), .*K3L=(.*)$", jline)

            # if we didn't match, just pass the line through
            if not mo:
                outfile.write(jline+'\n')
                continue

            if mo:
                if debug:
                    print('Matched, line ', jline)
                    print('group(1): ', mo.group(1))
                    print('group(2): ', mo.group(2))
                    print('group(3): ', mo.group(3))
                    print('group(4): ', mo.group(4))
                    print('group(5): ', mo.group(5))
                    print('group(6): ', mo.group(6))

            # Extract the element number to handle even and odd elements separately
            elem_digits = mo.group(1)
            parity = int(elem_digits)%2

            # Skip the nonphysical upstream multipole shims, wwhich are the 64 even + 66 odd ones in skipthese:
            primero_no_colon = "MPS"+mo.group(1)+mo.group(2)+"U"
            if debug: print("primero_no_colon: ", primero_no_colon)
            if primero_no_colon in skipthese:
                outfile.write(jline+'\n')
                if debug: print (f'Nonphysical: {jline}')
                continue

            if parity == 0:
                # these are even-parity multipoles
                if debug: print('even parity')
                outline = mo.expand(r"MPS\1\2U: \3, K1L=\4+VALUEFOR_K1L_EVEN, K2L=\5+VALUEFOR_K2L_EVEN, K3L=\6+VALUEFOR_K3L_EVEN, K4L=VALUEFOR_K4L_EVEN")
                if debug: print(outline)
                outfile.write(outline+'\n')
            else:
                # these are odd-parity multipoles
                if debug: print('odd parity')
                outline = mo.expand(r"MPS\1\2U: \3, K1L=\4+VALUEFOR_K1L_ODD, K2L=\5+VALUEFOR_K2L_ODD, K3L=\6+VALUEFOR_K3L_ODD, K4L=VALUEFOR_K4L_ODD")
                if debug: print(outline)
                outfile.write(outline+'\n')
