## Run test particles in Recycler lattice

The file `rr_modes.py` contains a module that will simulate 3 test particles
is the Recycler ring optionally setting sextupole `k2l` values
on specific magnets generating BPM data for 104 H and 104 V BPMs.
The saved data includes all phase space coordinates (position and momentum)
for the test particles for both H and V BPMs.

Usage:

```
python
import rr_modes
sext_options = {} # dict containing optional sextupole moments
# optionally set a sextupole value, for instance:
# sext_options['MPS109AD'] = 0.001
rr_modes.run_modes(sext_options, turns=2048)
```

