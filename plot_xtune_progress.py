import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib import rc
import os

plot_dir = "plots/"
if not os.path.exists(plot_dir):
    os.makedirs(plot_dir)

# Handle LaTeX in text, and tweak default font parameters
plt.rcParams['text.usetex'] = True
font = {'size'   : 12}
rc('font', **font)

Vals = np.loadtxt("tunefreq_fine.txt", skiprows=1, delimiter=",")
xtunes_target = Vals[:, 1]
ytunes_target = Vals[:, 2]

allF = np.load("allF.npy")
allX = np.load("allX.npy")
# Dictionary to interpret the values in X
IntMoms= {0:'K2L_H', 1:'K2L_V', 2:'K3L_H', 3:'K3L_V'} 
Jargon_dict = {'K2L':'Sextupole', 'K3L':'Octupole'}

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
show_params_and_sumsqerr = False # three little subplots at the top
max_iterations = 60
sumsq_history = np.empty(0)
for i, fvec in enumerate(allF[max_iterations:max_iterations+1]):
    i += max_iterations # FIXME don't leave this hack in place
    print (f'i: {i}')
    to_plot = fvec + np.hstack((xtunes_target, ytunes_target))
    
    fig = plt.figure(figsize=(8.9,6.4))
    if show_params_and_sumsqerr:
        (subfigs_up, subfig_main) = fig.subfigures(2, 1, wspace=0.5, height_ratios=[1., 2.2]) # 2 rows different heights, 1 col
        axmom_k2l, axmom_k3l, ax_overall = subfigs_up.subplots(1, 3, width_ratios=[1.,1.,1.]) # 1 row, unequal columns

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
            if intmom=='K2L': ax_mom.set_ylim(-0.002,+0.002)
            ax_mom.set_xlim(0, max_iterations+1)
            ax_mom.set_xticks(np.arange(0, max_iterations+1, step=10))
            ax_mom.set_title(f'{Jargon_dict[intmom]} Offsets')
            ax_mom.set_xlabel('Iteration', fontsize=16)
            ax_mom.legend()

        # Plot the overall performance
        sumsq_x = np.sum(np.square(xtunes_target - to_plot[:41]))
        sumsq_y = np.sum(np.square(ytunes_target - to_plot[41:]))
        sumsq = sumsq_x+sumsq_y
        sumsq_history = np.append(sumsq_history, sumsq)
        ax_overall.plot(range(i+1), sumsq_history, color='green')
        ax_overall.set_title('Sum Squared Error')
        ax_overall.set_yscale('log')
        ax_overall.set_ylim(1e-5, 5e-3)
        ax_overall.set_xlim(0, max_iterations+1)
        ax_overall.set_xticks(np.arange(0, max_iterations+1, step=10))
        ax_overall.set_xlabel('Iteration', fontsize=16)

    else:
        subfig_main = fig
        params = {'legend.fontsize': 'x-large',
                  'axes.labelsize': '24',
                  'axes.titlesize':'20',
                  'xtick.labelsize':'22',
                  'ytick.labelsize':'22'}
        plt.rcParams.update(params)

    # Plot the resulting chromaticity scan
    axs_main = subfig_main.subplots(1, 1)
    init_plot = allF[0]+ np.hstack((xtunes_target, ytunes_target))
    dp_o_p_scaler = 2.17667526e-6
    dp_o_p = Vals[:, 0] * dp_o_p_scaler
    axs_main.scatter(dp_o_p, Vals[:, 1]    , color='orange', label="measured xtune"   , marker='o'            )
    axs_main.plot   (dp_o_p, init_plot[:41], color='orange', label="initial xtune"  , linestyle='dotted'    )
    axs_main.plot   (dp_o_p, to_plot[:41]  , color='orange', label="simulated xtune", markerfacecolor='none')
    axs_main.scatter(dp_o_p, Vals[:, 2]    , color='blue'  , label="measured ytune"   , marker='o'            )
    axs_main.plot   (dp_o_p, init_plot[41:], color='blue'  , label="initial ytune"  , linestyle='dotted'    )
    axs_main.plot   (dp_o_p, to_plot[41:]  , color='blue'  , label="simulated ytune", markerfacecolor='none')
    plt.ylabel('Resonant tune')
    axs_main.set_ylim(0.31,0.46)
    plt.xlabel(r'Fractional Momentum Offset [$\frac{dp}{p}$]')
    axs_main.legend()
    plt.title("POUNDERS Iteration: " + str(i), y=0.93)
    plt.tight_layout()

    if show_params_and_sumsqerr: subfigs_up.subplots_adjust(bottom=0.30, top=0.80, hspace=0.2)
    
    plt.savefig(os.path.join(plot_dir, "Eval_" + str(i) + ".png"), dpi=200, bbox_inches="tight")
    plt.close()


