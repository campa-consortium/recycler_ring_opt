import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
#from matplotlib.animation import FuncAnimation, PillowWriter
import os

plot_dir = "plots/"
if not os.path.exists(plot_dir):
    os.makedirs(plot_dir)

Vals = np.loadtxt("tunefreq_fine.txt", skiprows=1, delimiter=",")
xtunes_target = Vals[:, 1]
ytunes_target = Vals[:, 2]

allF = np.load("allF.npy")
allX = np.load("allX.npy")
# Dictionary to interpret the values in X
IntMoms= {0:'K2L_H', 1:'K2L_V', 2:'K3L_H', 3:'K3L_V'} 

# Get max ranges of each group of parameter values
minmaxdict = {}
for int_i, intmom in IntMoms.items():
    # Get min and max range of "these" values
    these = allX.transpose()[int_i]
    this_min = these.min()
    this_max = these.max()
    # Lump together by moment order: K2L, K3L, etc
    mom_order = intmom[:-2]
    # Ensure dictionary entry exists, and fill it with initial values from "these"
    if not mom_order in minmaxdict.keys():
        minmaxdict[mom_order] = {'min':this_min, 'max':this_max}
    else:
        if this_min < minmaxdict[mom_order]['min']: minmaxdict[mom_order]['min'] = this_min
        if this_max > minmaxdict[mom_order]['max']: minmaxdict[mom_order]['max'] = this_max
    
# Loop over iterations, making plots
max_iterations = 60
sumsq_history = np.empty(0)
for i, fvec in enumerate(allF[:max_iterations+1]):
    print (f'i: {i}')
    fig = plt.figure(figsize=(8.4,6.4))
    (subfigs_up, subfig_main) = fig.subfigures(2, 1, wspace=0.5, height_ratios=[1., 2.7]) # 2 rows different heights, 1 col
    axmom_k2l, axmom_k3l, ax_overall = subfigs_up.subplots(1, 3, width_ratios=[1.,1.,2.]) # 1 row, unequal columns

    axmom_dict = {'K2L':axmom_k2l, 'K3L':axmom_k3l}
    # Plot the integrated moments up to the current iteration.
    ax_mom = None
    for int_i, intmom in IntMoms.items():
        mom_order = intmom[:-2] # 'K2L', 'K3L', etc.
        ax_mom = axmom_dict[mom_order]
        ax_mom.plot(range(i+1), allX.transpose()[int_i][:i+1], label=intmom)

    # Tidy up the axes
    for intmom, ax_mom in axmom_dict.items():
        ax_mom.set_ylim(minmaxdict[intmom]['min'], minmaxdict[intmom]['max'])
        ax_mom.set_xlim(0, max_iterations+1)
        ax_mom.set_title(f'{intmom} Parameters')
        ax_mom.legend()
    
    # Plot the overall performance
    to_plot = fvec + np.hstack((xtunes_target, ytunes_target))
    sumsq_x = np.sum(np.square(xtunes_target - to_plot[:41]))
    sumsq_y = np.sum(np.square(ytunes_target - to_plot[41:]))
    sumsq = sumsq_x+sumsq_y
    sumsq_history = np.append(sumsq_history, sumsq)
    ax_overall.plot(range(i+1), sumsq_history, color='green')
    ax_overall.set_title('Sum Sq. Difference')
    ax_overall.set_yscale('log')
    ax_overall.set_ylim(1e-5, 5e-3)
    ax_overall.set_xlim(0, max_iterations+1)

    # Plot the resulting chromaticity scan
    axs_main = subfig_main.subplots(1, 1)
    axs_main.scatter(Vals[:, 0], Vals[:, 1],   label="target xtune"   , marker='+'       )
    axs_main.plot   (Vals[:, 0], to_plot[:41], label="simulated xtune", markerfacecolor='none')
    axs_main.scatter(Vals[:, 0], Vals[:, 2],   label="target ytune"   , marker='+'       )
    axs_main.plot   (Vals[:, 0], to_plot[41:], label="simulated ytune", markerfacecolor='none')
    axs_main.set_ylim(top=0.46)
    plt.ylabel('Resonant tune')
    axs_main.set_ylim(0.31,0.46)
    plt.xlabel('RF Offset [Hz]')
    axs_main.legend()
    plt.title("Evaluation: " + str(i), y=0.94)
    plt.tight_layout()
    subfigs_up.subplots_adjust(bottom=0.15, top=0.80)
    
    plt.savefig(os.path.join(plot_dir, "Eval_" + str(i) + ".png"), dpi=200, bbox_inches="tight")
    plt.close()


