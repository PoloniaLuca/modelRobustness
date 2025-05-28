import matplotlib.pyplot as plt
import scipy.stats as stats
import numpy as np
from matplotlib.figure import Figure
from io import BytesIO
import urllib.parse
import base64
from matplotlib.patches import ConnectionPatch as cp


def plot_step_one(similarities, metrics, scatter=True):
    fig = Figure(figsize=(10,10), dpi=300)
    axs = fig.subplots(2)
    fig.subplots_adjust(hspace=0)
    std_x = np.std(similarities)
    std_y = np.std(metrics)
    ratio = std_y/std_x
    rho, p = stats.pearsonr(similarities, metrics)
    m, b = np.polyfit(similarities, metrics, 1)
    # base = b

    if scatter:
        axs[0].scatter(similarities, metrics)

    axs[0].plot([0,1], [b, m*1 + b], 'r', label='Regression Line (r = %.2f)' % rho)
    axs[0].legend(loc = 'upper left')
    axs[0].set_xlim(-0.05, 1.05)
    axs[0].set_ylim(np.min(metrics)-0.005, np.max(metrics)+0.01)
    x = [0, 0.5]
    y_w = np.array([0, 0.1*ratio/2]) + b
    y_m = np.array([0, 0.3*ratio/2]) + b
    y_s = np.array([0, 0.5*ratio/2]) + b
    y_vs = np.array([0, 0.7*ratio/2]) + b
    y_p = np.array([0, 1*ratio/2]) + b
    y_l = np.array([0, rho*ratio]) + b
    axs[1].plot([0,1], y_l, 'k--')
    p1a = [0, b]
    p2a = [1, m*1 + b]
    p1b = [0, y_l[0]]
    p2b = [1, y_l[1]]

    con1 = cp(xyA=p1a, xyB=p1b, coordsA="data", coordsB="data", axesA=axs[0], axesB=axs[1], color="gray", linestyle='dotted', alpha=0.2)
    axs[1].add_artist(con1)

    con2 = cp(xyA=p2a, xyB=p2b, coordsA="data", coordsB="data", axesA=axs[0], axesB=axs[1], color="gray", linestyle='dotted', alpha=0.2)
    axs[1].add_artist(con2)

    axs[1].plot(x, y_w, 'k', alpha= 0.2)
    axs[1].plot(x, y_m, 'k', alpha=0.4)
    axs[1].fill_between(x, y_w, y_m, color="crimson", alpha=0.2)
    axs[1].scatter(-1,-1, c="crimson", alpha= 0.2, edgecolor='black', label='Weak (0.1 < r < 0.35)')
 
    axs[1].plot(x, y_s, 'k', alpha=0.6)
    axs[1].fill_between(x, y_m, y_s, color="crimson", alpha=0.4)
    axs[1].scatter(-1,-1, c="crimson", alpha= 0.4, label='Moderate (0.3 < r < 0.5)')

    axs[1].plot(x, y_vs, 'k', alpha=0.8)
    axs[1].fill_between(x, y_s, y_vs, color="crimson", alpha=0.6)
    axs[1].scatter(-1,-1, c="crimson", alpha= 0.6, label='Strong (0.5 < r < 0.7)')

    axs[1].plot(x, y_p, 'k', alpha=1.0)
    axs[1].fill_between(x, y_vs, y_p, color="crimson", alpha=0.8)
    axs[1].scatter(-1,-1, c="crimson", alpha= 0.8, label='Very Strong (0.7 < r < 1.0)')
    
    axs[0].set_ylabel('Accuracy')
    axs[0].set_xticks([])
    axs[0].spines['bottom'].set_visible(False)

    axs[1].set_xlabel('Similarity')
    axs[1].set_xlim(-0.05, 1.05)
    axs[1].set_ylim(np.min(metrics)-0.005, np.max(metrics)+0.01)
    axs[1].set_yticks([])
    axs[1].spines['top'].set_visible(False)
    axs[1].legend(frameon=False, loc = 'lower center', bbox_to_anchor=(0.5, -0.27), ncol=2)
    
    img = BytesIO()
    fig.subplots_adjust(top=.99 , right=.99, left=0.08)
    fig.savefig(img, format="png") 
    img.seek(0)
    plot_data = urllib.parse.quote(base64.b64encode(img.read()).decode())
    return plot_data