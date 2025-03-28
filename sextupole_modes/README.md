## Simulate sextupole modes in the Recycler

### Files in this directory

| File | Use |
|:---------|:---------|
| RR2020V0922FLAT_k2l_template_NoBreaks_K2L_ready | Cooked Recycler lattice |
| RR_Chrom_Sextupoles.txt | Explanatory file on sextupoles in the ring |
| Read_TBT.ipynb | notebook demonstrating reading and displaying TBT data |
| RR_modified.txt | lattice file written out by run script after replacement of modified parameters |
| TBT_data.pickle | Output file from `convert_bpm_to_tbt.py` wcript |
| `cleaned_sext_names.pickle` | list of elements containing sextupole adjusters that are actually present in the lattice |
| `get_bpm_names.py` | convenience script to extract bpm element names from the lattice |
| `get_k2l_names.py` | convenience script to extract the names of k2l parameters to adjust from the start of the lattice file |
| `print_rr_elements.py` | convenience script to output all the elements in the RR lattice in csv format |
| `data_collection.txt` | part of a discussion on how to collect the data |
| `print_rr_kickers_and_shims.py` | convenience script to output the kickers, adjustment shims elements and BPMS in a csv file to assist in setting orbit bumps |
| `sext_names.pickle` | list of sextupole shims for adjustment created by `get_k2l_names.py` script |
| `rr_run_lattice.json` | written out by run script to record the lattice as simulated in the last run including all adjustments for run conditions |
| `rr_modes.py` | main run script for producing simulated BPM output |
| `rr_setup.py` | helper script to set up the Recycler simulation run |
| `rr_sextupoles.py` | helper script to adjust the Recycler harmonic sextupoles |
| `rr_qt60x.py` | helper script to set up the phase trombone to adjust the Recycler base tune |
| `tbt-format.odt` | information from Cris on the TBT data format |
| `sussix` | directory with the Xsuite python version of `sussix` NAFF package |

### How to run a simulation

```
import rr_modes

# The adjustment parameters are given as a dict with the
# adjustment values. An empty dict means use default unmodified
# values

params = {}
params['MPS100AD'] = -0.001

rr_modes.run_modes(params, turns=2048)
```

The output is written to `hdf5` files for each of the H or V BPMS such as
`BPM_hp100.h5`, `BPM_vp101.h5`, etc.

The script `convert_bpm_to_tbt.py` reads them all and write a TBT data file `TBT_data.pickle`.
