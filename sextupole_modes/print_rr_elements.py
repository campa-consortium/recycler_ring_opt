#!/usr/bin/env python

import sys, os
import numpy as np
import synergia

# Load the lattice saved from previous run
with open('rr_run_lattice.json', 'rb') as f:
    lattice = synergia.lattice.Lattice.load_from_json(f.read())

print('lattice #elements: ', len(lattice.get_elements()), ' ,length: ', lattice.get_length())

rrout = open('rr_lattice_elements.csv', 'w')

s = 0.0
print('s:name:type:length', file=rrout)
for elem in lattice.get_elements():
    print(f'{s}:{elem.get_name()}:{elem.get_type_name()}:{elem.get_length()}', file=rrout)
    s = s + elem.get_length()

rrout.close()
