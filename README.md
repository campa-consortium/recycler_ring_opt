# recycler_ring_opt

Run with the following command:

`python rr_noSC.py`

## To produce a template from a working lattice file:
By default, assumes the user wants to tweak K1L, K2L, K3L, and K4L for all ```MPS*U``` elements, separately for even and odd ones. 

```$ python3.9 templatize_latticefile.py --help                  
Usage: templatize_latticefile.py [-h] [-v] [--outfilename OUTFILENAME] [--element-regex ELEMENT_REGEX] [--split-by-parity SPLIT_BY_PARITY] LatticeFileIn

Create a template lattice file with placeholders.

positional arguments:
  LatticeFileIn         Required input file path

optional arguments:
  -h, --help            show this help message and exit
  -v, --debug           Verbose debugging output. (default:False)
  --outfilename OUTFILENAME
                        Output file name. (default= RR2020V0922_TEMPLATE_fixed)
  --element-regex ELEMENT_REGEX
                        String pattern to match. (default: "MPS*U")
  --split-by-parity SPLIT_BY_PARITY
                        Split elements even/odd. (default: True)```
