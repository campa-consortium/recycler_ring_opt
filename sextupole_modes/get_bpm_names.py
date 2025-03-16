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

    bpm_h_inst = []
    bpm_h_monitor = []
    bpm_v_inst = []
    bpm_v_monitor = []

    # Loop getting all elements with the proper name
    bpm_nm_patt = '(h|v)p[1-6][0-9][0-9]'
    pat = re.compile(bpm_nm_patt)

    for elem in lattice.get_elements():
        et = elem.get_type()
        ename = elem.get_name()
        #print(et, ': ', end='')
        if (et == ET.hmonitor) and pat.fullmatch(ename):
            bpm_h_monitor.append(elem)
        elif (et == ET.vmonitor) and pat.fullmatch(ename):
            bpm_v_monitor.append(elem)
        elif (et == ET.instrument) and pat.fullmatch(ename):
            if ename[0] == 'h':
                bpm_h_inst.append(elem)
            elif ename[0] == 'v':
                bpm_v_inst.append(elem)

    print(f'{len(bpm_h_monitor)} H monitors')
    print(f'{len(bpm_h_inst)} H instruments')
    print(f'{len(bpm_v_monitor)} V monitors')
    print(f'{len(bpm_v_inst)} V instruments')

    return

if __name__ == "__main__":
    main()

