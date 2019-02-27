import matplotlib.pyplot as plt
import numpy as np

def visualize_tapcorrection(D_pre, D_post, fs_act,
                            list_iois_pre, list_iois_post,
                            ind_sequence,
                            mu, sigma,
                            tolerance,
                            write_results, path_out):
    # visualization
    plt.figure(figsize=(15, 9))
    plt.subplot("211")
    _, clim = visualize_deviation_matrix(D_pre, fs_act, list_iois_pre)
    plt.plot((np.array(ind_sequence) - tolerance) / fs_act, color='k',linewidth=4)
    plt.plot((np.array(ind_sequence) - tolerance) / fs_act, color=[1,.6,.6])
    plt.subplot("212")
    visualize_deviation_matrix(D_post, fs_act, list_iois_post, clim=clim)
    fig = plt.gcf()
    fig.suptitle("mu=%04f, sigma=%04f" % (mu, sigma), fontsize=14)
    if write_results:
        plt.savefig(path_out[:-4] + ".png", dpi=300)
        plt.close()
    else:
        plt.draw()
        plt.show()

def visualize_deviation_matrix(S, fs_act, list_iois, xlim = None, clim = None, colorbar = True):
    from matplotlib.colors import LinearSegmentedColormap

    tolerance = int((S.shape[0] - 1)/2)
    left = -1 / 2
    right = S.shape[1] - 1 / 2
    lower = -tolerance / fs_act
    upper = tolerance / fs_act

    matrix_to_show = S.copy()
    matrix_to_show += 10**-1
    matrix_to_show[matrix_to_show<=0] = np.nan
    matrix_to_show -= 10**-1

    # get the colormap right
    log_comp = 100
    log_series = np.log((np.linspace(start=1, stop=log_comp, num=256)))
    min_val = 0.07
    scaled_series = log_series/np.max(log_series) * (1-min_val) + min_val
    gray_values = 1 - scaled_series
    gray_values_rgb = np.repeat(gray_values.reshape(256, 1), 3, axis=1)
    color_wb = LinearSegmentedColormap.from_list('color_wb', gray_values_rgb, N=256)

    im = plt.imshow(matrix_to_show,
                    aspect='auto',
                    extent=[left, right, lower, upper],
                    origin='lower',
                    cmap=color_wb)

    if colorbar:
        plt.colorbar()

    plt.plot(list_iois / 2, 'k')
    plt.plot(-list_iois / 2, 'k')

    plt.ylim([lower,upper])

    if xlim is not None:
        plt.xlim(xlim)

    if clim is not None:
        plt.clim(clim[0], clim[1])
    else:
        clim = plt.gci().get_clim()

    plt.xlabel('Tap index')
    plt.ylabel('Deviation (sec)')

    return im, clim