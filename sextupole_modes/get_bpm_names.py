#!/usr/bin/env python

# get BPM names of the form
#    HP[1-6][[0-9][0-9]
# and
#    VP[1-6][[0-9][0-9]

import sys, os
import numpy as np
import synergia
ET = synergia.lattice.element_type

import re
import pickle

lattice_file = '../RR2020V0922FLAT_k2l_template_NoBreaks_K2L_ready'
RR_line = "ring605_fodo"


def get_lattice(lattice_file, lattice_line):
    with open(lattice_file, 'r') as f:
        lattice_txt = f.read()

    reader = synergia.lattice.Mad8_reader()
    reader.parse_string(lattice_txt)

    lattice = reader.get_lattice(lattice_line)

    return lattice

def main():
    lattice = get_lattice(lattice_file, RR_line)

    # Loop getting all elements with the proper name
    bpm_nm_patt = '(h|v)p[1-6][0-9][0-9]'
    pat = re.compile(bpm_nm_patt)

    for elem in lattice.get_elements():
        et = elem.get_type()
        #print(et, ': ', end='')
        if (et == ET.hmonitor) or (et == ET.vmonitor) or (et == ET.instrument):
            print('found candidate: ', elem, end='')
            ename = elem.get_name()
            mo = pat.fullmatch(ename)
            if mo:
                print(elem, 'matched')
            else:
                print()
        # else:
        #     print()

    return

if __name__ == "__main__":
    main()
