#!/usr/bin/env python
import pickle

with open('sext_names.pickle', 'rb') as f:
    pn = pickle.loads(f.read())

print('type(pn): ', type(pn))
print(pn)
