# recycler_ring_opt

## Run the ```evaluate()``` function for a given parameter set, get the vectors of tune-vs-freq we want to match the data

After setting  PYTHONPATH so the Synergia modules are available:
```
[recycler_ring_opt]$ python
Python 3.9.16 (main, May 29 2023, 00:00:00) 
[GCC 11.3.1 20221121 (Red Hat 11.3.1-4)] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> 
>>> kxl_values = {
...         'K1L_EVEN': 0.01,
...         'K1L_ODD': -0.005,
...         'K2L_EVEN': -0.005,
...         'K2L_ODD': -0.00033,
...         'K3L_EVEN': 0.0000129,
...         'K3L_ODD': -0.0000333
...         }
>>> xtunes, ytunes = evaluate.evaluate(kxl_values)
generate_lattice, initial xtune:  0.44220778603001837 , ytune:  0.39154486215708884
Adjusting tunes to:
xtune:  0.4126
ytune:  0.356
delta_xtune:  -0.029607786030018346
delta_ytune:  -0.03554486215708885
Number of macroparticles: 41
Number of frequencies to run:  41
    offsets from  -0.004344974504652674 to 0.004344974504652674
Propagator: starting turn 1, final turn 1024

Propagator: turn    1/1024, time = 0.113s, macroparticles = (41) / ()
Propagator: turn    2/1024, time = 0.114s, macroparticles = (41) / ()
Propagator: turn    3/1024, time = 0.113s, macroparticles = (41) / ()

... skipping a bunch ...

Propagator: turn 1022/1024, time = 0.114s, macroparticles = (41) / ()
Propagator: turn 1023/1024, time = 0.113s, macroparticles = (41) / ()
Propagator: turn 1024/1024, time = 0.113s, macroparticles = (41) / ()
Propagator: total time = 125.475s
>>> xtunes
array([0.43633326, 0.43523356, 0.43411613, 0.43298387, 0.43183512,
       0.43067082, 0.4294961 , 0.42831135, 0.42711749, 0.42591224,
       0.42469878, 0.42348164, 0.42226021, 0.42103296, 0.41980236,
       0.41857286, 0.41734424, 0.41611508, 0.41488769, 0.41365023,
       0.41245057, 0.41124038, 0.41003644, 0.40884542, 0.4076643 ,
       0.40649495, 0.40533634, 0.404193  , 0.40306638, 0.40194496,
       0.40086651, 0.39979607, 0.39874633, 0.39771853, 0.39671478,
       0.39573646, 0.39478457, 0.3938603 , 0.39296507, 0.39210035,
       0.39126802])
>>> ytunes
array([0.39027933, 0.38848626, 0.38670575, 0.38493946, 0.38318761,
       0.38148277, 0.37971588, 0.37799436, 0.37628517, 0.37458575,
       0.37289381, 0.37120706, 0.36953048, 0.36785806, 0.36619437,
       0.36453058, 0.36287578, 0.36122213, 0.3595694 , 0.35791947,
       0.35626871, 0.35462432, 0.35297322, 0.35132475, 0.34967192,
       0.34801847, 0.34632388, 0.34469832, 0.34302883, 0.34135635,
       0.33967694, 0.33799013, 0.33629606, 0.33459307, 0.33287895,
       0.33115622, 0.3294218 , 0.32767607, 0.3259154 , 0.32414392,
       0.32235717])
>>> 
```

## To produce a template from a working lattice file:
By default, assumes the user wants to tweak K0L, K1L, K2L, and K3L for all physical ```MPS*U``` elements, separately for even and odd ones, and creates a set of eight MAD parameters accordingly. A list of nonphysical elements is hard-coded to be copied untouched into the template file as ```skipthese```. A set of initial values for these eight new MAD paramaeters is also hard-coded.

```
$ python3.9 templatize_latticefile.py --help                  
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
                        Split elements even/odd. (default: True)
```
## Generate a lattice file with a given set of parameters, from a template lattice file
``` 
$ python3.9 GenerateLatticeFile.py --help                                                                                 
usage: GenerateLatticeFile.py [-h] [-v] [--params PARAMS] [--outfilename OUTFILENAME] TemplateFileIn

Create a lattice file from a template.

positional arguments:
  TemplateFileIn        Required input file path.

optional arguments:
  -h, --help            show this help message and exit
  -v, --debug           Verbose debugging output. (default:False)
  --params PARAMS       comma-separated TOKEN:values pairs, e.g. REPLACEME_K1LEVEN:0.01,REPLACEME_K1ODDD:-0.23
  --outfilename OUTFILENAME
                        Output file name. (default= Built from input param choices,)


```

## rr_tune_survey.py runs the Recycler ring simulation.

A single bunch of 41 particles is launched at `dp/p` offsets corresponding to a frequency shift of `arange(-2000, 2050, 100)` Hz.

The turn-by-turn coordinates of each particle is saved in the HDF5 file `tracks.h5` in dataset named `track_coords`. This is an array of shape `(nturns, nparticles, 7)`. The run is currently set for 2000 turns so nturns = 2001 (initial + 2000). `nparticles` is 41 for a particle at each of the different momenta, and the third dimension are the phase space coordinates of the particle: `(x, x', y, y', cdt, dp/p, label)`.
 
This output can be easily read with the `h5py` python module.
