import argparse
import glob
import os
import time
import re
from collections import Counter


# global variables
_CURR_DIR = os.path.dirname(os.path.abspath(__file__))
regexpattern = re.compile(r'^MP.*K2L=') # Starts "MP[zero or more characters]K2L="

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Read in and analyze a lattice file')
    parser.add_argument("LatticeFileIn", help="Required input file path")
    parser.add_argument('-v','--debug', action='store_true', dest='debug', default=False,
                        help='Verbose debugging output. (default:False)')
    parser.add_argument("--outfilename", dest="outfilename", default='',
                        help='Output file name. (default= )')

    # read command-line arguments into variables
    args = parser.parse_args()
    infilename  = args.LatticeFileIn
    outfilename = args.outfilename
    debug       = args.debug
    if outfilename == '': outfilename = infilename+'_K2L_ready'

    # First pass over the file: collect the list of lattice elements whose declarations will be modified
    K2Loffset_by_element_of_interest = {}
    K2L_devs = []
    with open(infilename,'r') as flatfile:
        if debug: print (f'Reading input file {infilename}.')
        lines = flatfile.readlines()
        if debug: print (f'Read {len(lines)} lines.')
        for line in lines:                
            #if not line.count('K2L=') > 0: continue
            if not regexpattern.match(line): continue
            if debug: print ('Matched: ',line)
            primero = line.split(':')[0]
            # Dictionary with element-name keys and offset-name values
            K2Loffset_by_element_of_interest[primero] = f'{primero}_K2L_offset' 
            primero_stars = re.sub('\d', '*', primero)
            if debug: print (primero_stars)
            K2L_devs.append(primero_stars)
    # Summarize how many of each pattern we found
    pattern_counts = Counter(K2L_devs)    
    pattern_count_pop = 0
    for key in sorted (pattern_counts.keys()):
        print (key, ': ', pattern_counts[key])
        pattern_count_pop += pattern_counts[key]
    # Print total counts of list and set
    print (f'Found {pattern_count_pop} elements and {len(K2Loffset_by_element_of_interest)} unique among them.')
    if not pattern_count_pop == len(K2Loffset_by_element_of_interest): exit ('Hey! Nonunique elements may cause undesired behavior.')
    
    # OK, ready to re=process the input file and this time write out the new file
    lastlinewascomment = False
    with open(infilename,'r') as flatfile, open(outfilename, 'w') as outfile:
        if debug: print (f'Reading input file {infilename}.')
        lines = flatfile.readlines()
        if debug: print (f'Read {len(lines)} lines.')
        for line in lines:                
            if line.startswith('!'):
                lastlinewascomment = True
                outfile.write(line)
                continue
            if lastlinewascomment:
                lastlinewascomment = False
                print (line)
                # Write out the new lines we want to add.
                for EOI, offsetname in K2Loffset_by_element_of_interest.items():
                    outfile.write(f'{offsetname}:= 0.0\n')
                # And THEN write out this line we're on.
                outfile.write(line)
                continue
            if regexpattern.match(line):
                lineparts = line.split(',')
                elementname = lineparts[0].split(': ')[0]
                newparts = []
                for part in lineparts:
                    # Pass through all the non-K2L 
                    if part.count('K2L=')==0:
                        newparts.append(part)
                        continue
                    # Otherwise, add in our little offset term
                    # JMSJ catch the case like K2L=0.9 which do not have an operator at the front of the numerical expression!
                    if not part.split('K2L=')[1].startswith('-'):
                        operator = '+'
                    else: operator = ''
                    newpart = part.replace('K2L=', f'K2L={K2Loffset_by_element_of_interest[elementname]}{operator}')
                    print (f'Created new part {newpart}')
                    newparts.append(newpart)
            
                outfile.write(''.join(newparts))
            else: outfile.write(line)
            
