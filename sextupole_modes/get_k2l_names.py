#!/usr/bin/env python
import sys, os
import numpy as np
import re
import pickle

lat_file_name = "../RR2020V0922FLAT_k2l_template_NoBreaks_K2L_ready"

mp_pattern = '^(MP.*)_K2L_offset:= 0.0$'

sext_names = []

f = open(lat_file_name, 'r')
for l in f.readlines():
    mo = re.match(mp_pattern, l)
    if mo:
        nm = mo.group(1)
        print('matched: ', nm)
        sext_names.append(nm)
f.close()

print('found ', len(sext_names), ' multipoles')

print(sext_names)

with open('sext_names.pickle', 'wb') as p:
    pickle.dump(sext_names, p)

sys.exit(0)
