#!/usr/bin/env python

import sys, os
import numpy as np
import synergia
import pickle

import rr_modes

# Load the lattice saved from previous run
#with open('rr_run_lattice.json', 'rb') as f:
#    lattice = synergia.lattice.Lattice.load_from_json(f.read())

# Load the lattice as if running
lattice = rr_modes.prepare_lattice({})

sext_names = rr_modes.sext_names

# downcase all the sext_names
for i in range(len(sext_names)):
    sext_names[i] = sext_names[i].lower()

print('lattice #elements: ', len(lattice.get_elements()), ' ,length: ', lattice.get_length())

print(len(sext_names), ' corrector elements')


elem_name_cnt = {}
elem_name_map = {}
for elem in lattice.get_elements():
    ename = elem.get_name()
    if ename in elem_name_cnt:
        elem_name_cnt[ename] = elem_name_cnt[ename] + 1
    else:
        elem_name_cnt[ename] = 1
        elem_name_map[ename] = elem

# Any element names duplicated?
dupnames = [ k for k in elem_name_cnt.keys() if elem_name_cnt[k] > 1 ]
print('dupnames: ', dupnames)

# check if adjustment parameters elements are present in the lattice
fixed_sext = sext_names[:]
not_present = []
for sname in sext_names:
    if sname not in elem_name_map:
        #print('Adjuster name ', sname, ' not present in lattice')
        not_present.append(sname)
        fixed_sext.remove(sname)

print(len(fixed_sext), ' adjusters remaining after removing non present elements')
with open('cleaned_sext_names.pickle', 'wb') as f:
      pickle.dump(fixed_sext, f)
print(fixed_sext)

print()
print()
print(len(not_present), ' adjusters not present')
print(not_present)
