import numpy as np
import matplotlib.pyplot as plt
import os

plot_dir = "plots/"
if not os.path.exists(plot_dir):
    os.makedirs(plot_dir)

Vals = np.loadtxt("tunefreq_fine.txt", skiprows=1, delimiter=",")
xtunes_target = Vals[:, 1]
ytunes_target = Vals[:, 2]

allF = np.load("allF.npy")
allX = np.load("allX.npy")

for i, fvec in enumerate(allF[:60]):
    fig, ax1 = plt.subplots()

    to_plot = fvec + np.hstack((xtunes_target, ytunes_target))

    ax1.plot(Vals[:, 0], Vals[:, 1], label="target xtune")
    ax1.scatter(Vals[:, 0], to_plot[:41], label="simulated xtune")

    ax1.plot(Vals[:, 0], Vals[:, 2], label="target ytune")
    ax1.scatter(Vals[:, 0], to_plot[41:], label="simulated ytune")
    ax1.legend()
    plt.title("Evaluation: " + str(i))

    left, bottom, width, height = [0.05, 0.05, 0.2, 0.2]
    ax2 = fig.add_axes([left, bottom, width, height])
    ax2.scatter(range(4), allX[i], color="green")
    ax2.set_ylim(-1, 1)
    ax2.set_yticks([-1, 0, 1], ["LB", 0, "UB"])
    ax2.set_xticks([0, 1, 2, 3], ["2_e", "2_o", "3_e", "3_o"])

    # plt.savefig(os.path.join(plot_dir, "Eval_" + str(i) + ".png"), dpi=200, bbox_inches="tight", transparent=True)
    plt.savefig(os.path.join(plot_dir, "Eval_" + str(i) + ".png"), dpi=200, bbox_inches="tight")
    plt.close()


