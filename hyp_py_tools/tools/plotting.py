
def set_aspect(ax,ratio: int=0.666):
    xleft, xright = ax.get_xlim()
    ybottom, ytop = ax.get_ylim()
    ax.set_aspect(abs((xright - xleft) / (ybottom - ytop)) * ratio)


#RGB colors for plotting
scientific_colors = [
    (0.9, 0.36, 0.054),
    (0.365248, 0.427802, 0.758297),
    (0.945109, 0.593901, 0.),
    (0.645957, 0.253192, 0.685109),
    (0.285821, 0.56, 0.450773),
    (0.7, 0.336, 0.),
    (0.491486, 0.345109, 0.8),
    (1, 0, 0),
    (0, 1, 0),
(0, 0, 1),
(1, 1, 0),
(1, 0, 1),
(1, 0, 0),
(1, 0, 1)

]

scientific_colors_255 = [(int(x[0]*255),
                          int(x[1]*255),
                          int(x[2]*255))
                         for x in scientific_colors]



def set_plotting_defaults(plt):
    plt.rcParams["font.family"] = "Arial"
    plt.rcParams["legend.frameon"] = False
    plt.rcParams["legend.framealpha"] = 1
    plt.rcParams["legend.fancybox"] = False
    plt.rcParams['figure.figsize'] = 10, 7.5


def make_nice_plot(ax, x_label: str, y_label: str, ax_ratio = 0.666) -> None:
    ax.set_xlabel(x_label, size=15, labelpad = 7, family='Arial')
    ax.set_ylabel(y_label, size=15, labelpad = 7, family='Arial')
    set_aspect(ax, ax_ratio)
    ax.tick_params(direction="in", labelsize=12, pad = 7)


