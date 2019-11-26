import readwrite
import activation
import numpy as np

def correct_taps(path_taps, path_audio,
                 max_deviation=50,
                 fs_act = 100,
                 method_act_curve = 'madmom',
                 method_sequence_computation = 'dtw',
                 lambda_transition = .1,
                 visualize = True,
                 write_results = False,
                 path_out = None,
                 save_actcurves = False):

    if write_results:
        assert path_out is not None

    # load taps
    counts_taps, time_taps = readwrite.read_beat_annotation(path_taps)

    # compute activation curve
    if method_act_curve == 'novelty':
        act = activation.compute_novelty_act_curve(path_audio, load_act=True, save_act=save_actcurves)
    elif method_act_curve == 'madmom':
        act = activation.compute_madmom_act_curve(path_audio, load_act=True, save_act=save_actcurves)
    else:
        raise Exception('Unknown method: ' + method_act_curve)

    # compute deviation matrix
    D_pre, list_iois_pre = compute_deviation_matrix(act, time_taps, fs_act, max_deviation)

    # compute deviation sequence
    if method_sequence_computation == 'dtw':
        dev_sequence = compute_score_maximizing_dev_sequence(D_pre, lambda_transition)
    elif method_sequence_computation == 'max':
        dev_sequence = compute_framewise_maximizing_dev_sequence(D_pre)
    else:
        raise Exception('Unknown method: ' + method_sequence_computation)

    # derive corrected beat positions
    final_beat_times, mu, sigma = convert_dev_sequence_to_corrected_tap_times(dev_sequence, time_taps, max_deviation, fs_act)

    if write_results:
        readwrite.write_beat_annotation(counts_taps, final_beat_times, path_out)

    if visualize:
        import visualization as vis
        D_post, list_iois_post = compute_deviation_matrix(act, final_beat_times, fs_act, max_deviation)

        vis.visualize_tapcorrection(D_pre, D_post, fs_act,
                                    list_iois_pre, list_iois_post,
                                    dev_sequence,
                                    mu, sigma,
                                    max_deviation,
                                    write_results, path_out)

    return counts_taps, final_beat_times, mu, sigma


def convert_dev_sequence_to_corrected_tap_times(dev_sequence, time_taps, tolerance, fs_act):
    final_beat_times = []
    delta_list = []
    for i, t in enumerate(time_taps):
        delta = (dev_sequence[i] - tolerance) / fs_act
        delta_list.append(delta)
        final_beat_times.append(t + delta)
    return np.array(final_beat_times), np.mean(np.array(delta_list)), np.std(np.array(delta_list))


def compute_score_maximizing_dev_sequence(D, lambda_transition):
    # go to log-prob domain
    eps = 10 ** -17
    P = np.log(D + eps)

    # computation transition-matrix
    T = np.zeros((P.shape[0], P.shape[0]))
    for i in range(P.shape[0]):
        for j in range(P.shape[0]):
            T[i, j] = compute_state_change_prob(i, j, lambda_transition=lambda_transition)
    T = np.log(T)
    assert not np.any(np.isnan(T))

    # forward pass
    A = np.ones(P.shape) * -np.inf # accumulated probability matrix
    A[:, 0] = P[:, 0]
    O = np.ones(P.shape) * -np.inf # origin matrix
    O[:, 0] = 0
    for j in range(1, A.shape[1]):
        assert np.any(np.array(A[:, j - 1]) > -np.inf)
        assert not np.all(np.isnan(P[:,j]))
        for ind_to in range(A.shape[0]):
            if np.isnan(P[ind_to, j]):
                continue
            for ind_from in range(A.shape[0]):
                if np.isnan(P[ind_from, j - 1]):
                    continue
                curr_prob = A[ind_from, j - 1] + T[ind_from, ind_to] + P[ind_to, j]
                if curr_prob > A[ind_to, j]:
                    A[ind_to, j] = curr_prob
                    O[ind_to, j] = ind_from

    # backward pass
    ind = A.shape[1] - 1
    max_ind = np.argmax(A[:, ind])
    dev_sequence = []
    while ind >= 0:
        dev_sequence = [max_ind] + dev_sequence
        max_ind = int(O[max_ind, ind])
        ind -= 1

    return dev_sequence


def compute_state_change_prob(ind_from, ind_to,lambda_transition = 1):
    return np.exp(-lambda_transition * np.abs(ind_from-ind_to))


def compute_framewise_maximizing_dev_sequence(S):
    return np.nanargmax(S,axis=0)


def compute_deviation_matrix(beat_activation, beat_times, fs_act, tolerance):
    D = np.ones((2 * tolerance + 1, len(beat_times))) * np.inf
    list_iois = []
    for i, t in enumerate(beat_times):
        segment_act = np.zeros(2 * tolerance + 1)
        ind_act = int(np.round(t * fs_act))

        if ind_act < 0 or ind_act >= beat_activation.shape[0]:
            print("WARNING: Tap at %.02fs is outside of the audio's duration" % t)
            continue

        ind_act_start = np.max((0, ind_act - tolerance))
        ind_act_end = np.min((beat_activation.shape[0], ind_act + tolerance + 1))
        ind_segment_start = tolerance - (ind_act - ind_act_start)
        ind_segment_end = len(segment_act) - (ind_act + tolerance - ind_act_end + 1)
        segment_act[ind_segment_start:ind_segment_end] = beat_activation[ind_act_start:ind_act_end]
        curr_ioi_sec = compute_curr_ioi(beat_times, i)
        curr_ioi_frames = int(np.round(curr_ioi_sec * fs_act))
        list_iois.append(curr_ioi_sec)
        pad_len = int(np.floor((len(segment_act) - curr_ioi_frames) / 2))
        pad_len = np.min((pad_len,tolerance)) # to avoid all-nan columns
        if pad_len > 0:
            segment_act[:pad_len] = np.nan
            segment_act[-pad_len:] = np.nan
            segment_act[pad_len:-pad_len] *= my_hann(len(segment_act[pad_len:-pad_len]))
        else:
            segment_act *= my_hann(len(segment_act))

        assert not np.all(np.isnan(segment_act))
        D[:, i] = segment_act
    return D, np.array(list_iois)


def compute_curr_ioi(ts_taps,ind):
    if ind == 0:
        ioi = ts_taps[ind+1]-ts_taps[ind]
    else:
        ioi = ts_taps[ind]-ts_taps[ind-1]
    return ioi


def my_hann(n):
    w = np.hanning(n+2)
    return w[1:-1]