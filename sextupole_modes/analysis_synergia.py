import numpy as np
import json
import matplotlib.pyplot as plt
import matplotlib as mpl
import glob
import pickle
# import h5py
import pprint

import matplotlib as mpl
mpl.rcParams['mathtext.fontset'] = 'cm'
mpl.rcParams['font.family'] = 'STIXGeneral'

# Import files if no pip install
# Comment out if succesfully did pip install
import sys
sys.path.append('../tbtFit_sim/')
sys.path.append('../tbtFit_sim/sussix')
import tbtFitsim as tbtFit_sim # as tbtFit_sim
import rdt_calculation
from pathlib import Path
# Attempt to silence Pandas when adding columns to slices of dataframes
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'

default_rdt_spectra_filename = 'RDTS_spectra_BPM.pickle'
import argparse
parser = argparse.ArgumentParser(prog='analysis_synergia')
parser.add_argument('--debug', '-v', dest='debug', action='store_true',
                    help='Verbose debugging output. (default: false)')
parser.add_argument('--BPM', dest='BPMkey', default="412",
                    help='A single BPM designation to process for RDT contributions,')
parser.add_argument('--regen-rdts', dest='regen_rdts', action='store_true',
                    help='Regenerate RDT spectrum files. (default: false)')
parser.add_argument('--rdts-filename', dest='rdts_filename', default=default_rdt_spectra_filename,
                    help='Verbose debugging output.')

args = parser.parse_args()
debug         = args.debug
BPMkey        = args.BPMkey
rdts_filename = args.rdts_filename
regen_rdts    = args.regen_rdts

if BPMkey.count('R:')==0:
    if int(BPMkey)%2 ==0: BPMkey = f'R:HP{BPMkey}'
    else:                 BPMkey = f'R:VP{BPMkey}'

saveout_filename_str = Path(rdts_filename).name
saveout_filename_str = saveout_filename_str.replace('.pickle','') + f'_at{BPMkey}'.replace(':','')
savout_dir = Path(rdts_filename).parent

if debug: print (f'Saveout to :{savout_dir}')


with open(rdts_filename, 'rb') as f:
    tbt_data = pickle.load(f)
    
if debug:
    for i, eachdict in enumerate(tbt_data):
        print (f'List element {i} has keys: ',eachdict.keys())
        #pprint.pp (tbt_data)

# Import BPM data from simulated data
# and create tbtFit instance
fit_h = tbtFit_sim.tbtFit(bpmdict=tbt_data[0], matrixFile='transferMatSynergia.txt', plane='H', windowBPMs = 10, verbose = False)
fit_h.zerosAverage()
fit_h.latticeScan(window=[5,100])
fit_h.mask_bad_fits()

if debug:
    for BPM, fit in fit_h.bpm_fit.items():
        xmin, xmax = fit["x"].min(), fit["x"].max()
        pxmin, pxmax = fit["xp"].min(), fit["xp"].max()
        if xmax-xmin > 1e-21 or pxmax-pxmin > 1e-21: print (BPM, f'Min/Max found values of x, p_x: [{xmin:.2E}/{xmax:.2E}], [{pxmin:.2E}/{pxmax:.2E}]')

#BPMkey = 'R:HP404'
#BPMkey = 'R:HP212'

# Render visualization of orbit at BPMkey location
fig, ax = plt.subplots(figsize=(50,10))
plt.plot(fit_h.bpm_fit[BPMkey]['x'])
ax2 = ax.twinx()
plt.plot(fit_h.bpm_fit[BPMkey]['xp'])
#plt.plot(fit_h.data[BPMkey]['x_mean'],alpha = 0.2)
fig.savefig(f"Orbit{BPMkey}_{saveout_filename_str}.png")

# Render visualization of phase space visitations at BPMkey location
fig, ax = plt.subplots(figsize=(20,10))
plt.scatter(fit_h.bpm_fit[BPMkey]['x_norm'],fit_h.bpm_fit[BPMkey]['xp_norm'],s = 1)
fig.savefig(f"PhaseSpace{BPMkey}_{saveout_filename_str}.png")

# Compute RDTs
print (f'About to start rdt_calculation.RDTcalculation1D()...')
rdts = rdt_calculation.RDTcalculation1D(fit = fit_h)
print (f'    Done. rdts object is now: {rdts}')

# Check to see if we can load pre-calculated RDT spectra file.
# First get the filename for this BPM's RDT spectrum file, if not yet specified
if rdts_filename == default_rdt_spectra_filename:
    rdts_filename = default_rdt_spectra_filename.replace('BPM', f'{BPMkey}')

rdt_spectra_filename = f'{savout_dir}/Spectra_{saveout_filename_str}.pickle'
print(f'  rdt_spectra_filename = {rdt_spectra_filename}.')


# If we're (re)generating the file of spectra:
if regen_rdts or not Path(rdt_spectra_filename).is_file(): 
    print (f'About to start rdts.get_spectrum_bpms()...')
    rdts.get_spectrum_bpms(number_of_harmonics=1000, doonly=[412]) #, trunc=2)
    with open(rdt_spectra_filename, 'wb') as rdt_file:
        pickle.dump(rdts, rdt_file)
    print (f'    Done.')
else:
    if Path(rdt_spectra_filename).is_file():
        with open(rdt_spectra_filename, 'rb') as rdt_file:
            rdts = pickle.load(rdt_file)
    else: exit (f'Unable to load {rdt_spectra_filename}.  Want to (re)generate it?')

absfunc = lambda row: np.abs(row['amplitude'])
print (f'Spectra in dictionary with keys: {list(rdts.spectrums.keys())}')
dfforqx = rdts.spectrums[BPMkey]['spectrum']['x'].copy()

qx = np.abs(dfforqx.iloc[dfforqx.apply(absfunc,axis=1).idxmax()]['frequency'])
qy = 0.463608

if debug: print (f'Tunes (qx, qy)= ({qx},{qy})')

rdt_spectra_lines_filename = rdt_spectra_filename.replace('Spectra_', 'Spectra_Lines_')
# Calculate resonance lines
if regen_rdts or not Path(rdt_spectra_lines_filename).is_file(): 
    print (f'About to start rdts.get_lines()...')
    rdts.get_lines(error_tol=0.001,fundamental_tunes = [qx,qy])
    # ..and update the file with the updated rdts object
    with open(rdt_spectra_lines_filename, 'wb') as rdt_file:
        pickle.dump(rdts, rdt_file)
    print (f'    Done.')
else:
    print (f'Expecting that rdts.get_lines() has already been run for {BPMkey} xlines:')
    if Path(rdt_spectra_lines_filename).is_file():
        with open(rdt_spectra_lines_filename, 'rb') as rdt_file:
            rdts = pickle.load(rdt_file)
    else: exit (f'Unable to load {rdt_spectra_lines_filename}.  Want to (re)generate it?')
    if debug: print (rdts.spectrums[BPMkey]['xlines'])

# Which horizontal-plane spectral lines are there?
complete_3_list = []
for j in [0,1,2,3]:
    for k in [0,1,2,3]:
        for l in [0,1,2,3]:
            for m in [0,1,2,3]:
                if j+k+l+m == 3:
                    complete_3_list.append((j,k,l,m))
jklm_list = [(3,0,0,0), (2,0,1,0), (1,0,2,0), (0,0,3,0)]
ThirdOrderLines = rdts.spectrums[BPMkey]['xlines'].loc[rdts.spectrums[BPMkey]['xlines'].jklm.isin(complete_3_list)]
#print (rdts.spectrums[BPMkey]['xlines'].where(rdts.spectrums[BPMkey]['xlines'].jklm == (3,0,0,0)))
# pre-calculate all the magnitudes and phases of these amplitudes
ThirdOrderLines['magnitude'] = np.abs(ThirdOrderLines['amplitude'])
ThirdOrderLines['phase'] = np.angle(ThirdOrderLines['amplitude'])
print (ThirdOrderLines)


# plot measured RDTs, with visual call-outs for the ones we're focusing on
fig, ax = plt.subplots(figsize=(20,10))
plt.scatter(rdts.spectrums[BPMkey]['spectrum']['x']['frequency'],np.abs(rdts.spectrums[BPMkey]['spectrum']['x']['amplitude']),s = 15,color = 'orange', alpha=0.8)
#plt.stem(rdts.spectrums[BPMkey]['xlines']['frequency'],np.abs(rdts.spectrums[BPMkey]['xlines']['amplitude']))
plt.stem(ThirdOrderLines['frequency'], ThirdOrderLines['magnitude'], markerfmt='x')
plt.yscale('log')
plt.xlim(-0.5, 0.5)
plt.ylim(1.0e-09, 5.0e-03)
plt.xticks(fontsize=24)
plt.yticks(fontsize=24)
plt.title(BPMkey, fontsize = 30)
plt.xlabel(r'Horizontal Fractional Tune',fontsize = 30)
plt.ylabel(r'Amplitude $\left[ \, \text{m}^{1/2}\,\right]$',fontsize = 30)

for row_i in ThirdOrderLines.index:
    row = ThirdOrderLines.loc[row_i]
    # Knit a string to label this point...
    text_str = f"(j,k,l,m)={row['jklm']}\nFreq:{row['frequency']:.2f}\n$M$: {row['magnitude']:.3e} $\phi$: {row['phase']:.3e}"
    # ..and place it nearby, just a small, consistent offset away
    plt.text(row['frequency']+0.01, np.abs(row['amplitude'])*1.05, text_str, fontsize=25) 
fig.savefig(f'Resonance_Spectrum_at_{BPMkey.replace(":","")}_{saveout_filename_str}.png')

