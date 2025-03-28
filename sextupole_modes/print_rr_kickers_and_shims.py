#!/usr/bin/env python

import sys, os
import numpy as np
import synergia
import re
import pickle

ET = synergia.lattice.element_type

# Load the lattice saved from previous run
with open('rr_run_lattice.json', 'rb') as f:
    lattice = synergia.lattice.Lattice.load_from_json(f.read())

print('lattice #elements: ', len(lattice.get_elements()), ' ,length: ', lattice.get_length())

# load the list of elements with shims
with open('sext_names.pickle', 'rb') as f:
    sext_elems = pickle.loads(f.read())
print('Found ', len(sext_elems), ' elements with shims')    
print(sext_elems[:10])
# Set them all to lowercase to match the lattice names
for n in range(len(sext_elems)):
    sext_elems[n] = sext_elems[n].lower()
print(sext_elems[:10])

rrout = open('rr_interesting_elements.csv', 'w')

s = 0.0
nsextelem = 0
nhmon = 0
nvmon = 0
nhkick = 0
nvkick = 0

print('s:name:type:length', file=rrout)
for elem in lattice.get_elements():
    found = False

    ename = elem.get_name()
    etype = elem.get_type()

    if ename in sext_elems and etype == ET.multipole:
        # is this element one of the adjustable shims?
        # yes this one is there
        found = True
        nsextelem = nsextelem + 1

    # is this a hkicker
    elif re.fullmatch('h[1-6][0-9][0-9]', ename) and etype == ET.hkicker:
        found = True
        nhkick = nhkick + 1
    # is this a vkicker
    elif re.fullmatch('v[1-6][0-9][0-9]', ename) and etype == ET.vkicker:
        found = True
        nvkick = nvkick + 1
    # is this a BPM of the correct type?
    elif re.fullmatch('hp[1-6][0-9][0-9]', ename) and etype == ET.hmonitor:
        found = True
        nhmon = nhmon + 1
    elif re.fullmatch('vp[1-6][0-9][0-9]', ename) and etype == ET.vmonitor:
        found = True
        nvmon = nvmon + 1

    if found:
        print(f'{s}:{elem.get_name()}:{elem.get_type_name()}:{elem.get_length()}', file=rrout)

    s = s + elem.get_length()

print('nsextelem: ', nsextelem)
print('nhmon: ', nhmon)
print('nvmon: ', nvmon)
print('nhkick: ', nhkick)
print('nvkick: ', nvkick)
      

rrout.close()

