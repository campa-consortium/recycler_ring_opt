import argparse
import glob
import os
import time
from collections import Counter

# parse arguments
parser = argparse.ArgumentParser(
    description='Create a lattice file from a template.')
parser.add_argument("TemplateFileIn", help="Required input file path.")
parser.add_argument('-v','--debug', action='store_true', dest='debug', default=False,
                   help='Verbose debugging output. (default:False)')
parser.add_argument('--params', dest='params',
                    type=lambda e: {k:float(v) for k,v in (x.split(':') for x in e.split(','))},
                    help='comma-separated TOKEN:values pairs, e.g. REPLACEME_K1LEVEN:0.01,REPLACEME_K1ODDD:-0.23'
                    )
parser.add_argument("--outfilename", dest="outfilename", default='',
                    help='Output file name. (default= Built from input param choices,)')
# global variables
_CURR_DIR = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    # read arguments
    args = parser.parse_args()
    infilename  = args.TemplateFileIn
    debug       = args.debug
    params      = args.params
    outfilename = args.outfilename

    # By default, outfilename is the null string, as a signal value
    if outfilename == '':
        outfilename = infilename
        # Craft a better file name from the params.
        # Ex: GenerateLatticeFile.py RR2020V0922_TEMPLATE_fixed --params REPLACEME_K1LEVEN:0.01,REPLACEME_K1ODDD:-0.23
        #     ---> RR2020V0922_K1LEVENpos0.01_K1LODDDneg0.23_fixed
        if outfilename.count('TEMPLATE')>0:
            betterstring = '' # What to replace TEMPLATE with
            for k,v in sorted(params.items()): #loop through any params given, in sorted order..
                betterkey = k.replace('REPLACEME_','') # ...delete this part of the param, if present
                # Signify value sign with a three-letter shorthand for readability
                signword = 'pos'
                if v<0.0:  signword = 'neg'
                # Then put it all together, like "K1LEVENneg0.01_"
                betterstring += betterkey+signword+ str(v).replace('-','',1) + '_'
            # Chop off that final _
            betterstring = ''.join(betterstring.rsplit('_',1))
            outfilename = outfilename.replace('TEMPLATE',betterstring) # ok, at last, replace
        if debug: print (outfilename)
                    
    # Simple, ordered replacements of parameter tokens with values
    with open(infilename,'r') as infile, open(outfilename, 'w') as outfile:
        if debug: print (f'Reading input file {infilename} to make output template file {outfilename}')

        lines = infile.readlines()
        if debug: print (f'Read {len(lines)} lines.')
        # Loop the lines, replacing token in order, heedlessly
        for line in lines:
            outline = line
            for k,v in sorted(params.items()):
                outline = outline.replace(k,str(v))
            if debug and outline != line: print (outline)
            outfile.write(outline)
