from madmom.features.downbeats import RNNDownBeatProcessor
import librosa
import numpy as np
import pickle
import os

def compute_madmom_act_curve(path_audio_full, load_act = False, save_act = False):
    path_pickle = path_audio_full[:-4] + '_madmomact.pickle'
    if load_act and os.path.exists(path_pickle):
        act = pickle.load(open(path_pickle, 'rb'))
    else:
        act_processor = RNNDownBeatProcessor()
        x, fs = librosa.load(path_audio_full, sr=44100)
        act = act_processor.process(x)
        if save_act:
            pickle.dump(act,open(path_pickle, 'wb'))
    act = act[:,0] + act[:,1] # accumulate beat and down-beat activation curves
    return act

def compute_novelty_act_curve(path_audio_full, load_act = False, save_act = False):
    path_pickle = path_audio_full[:-4] + '_noveltyact.pickle'
    if load_act and os.path.exists(path_pickle):
        act = pickle.load(open(path_pickle, 'rb'))
    else:
        # signal
        x, fs = librosa.load(path_audio_full, sr=44100)

        # Short-time Fourier Transform
        spec,_,_ = stft(x,fs=44100,win_len=1024,fps=100)

        # apply logarithmic compression
        logspec = np.log(1 + 100*np.abs(spec))

        # normalize
        normspec = logspec/(np.max(logspec) * logspec.shape[0] + 10**-17)

        # compute first order derivative
        deltaspec = np.concatenate((np.zeros((normspec.shape[0],1)),(normspec[:,1:] - normspec[:,:-1])),axis=1)

        # keep only positive derivatives
        rectspec = np.maximum(np.zeros(deltaspec.shape), deltaspec)

        # sum up to form novelty curve
        act = np.sum(rectspec,axis=0)

        # subsrtact local average
        kernel = np.ones(20)/20
        localavg = np.convolve(act,kernel,mode='same')

        # substract local average anddo half-wave rectification
        act = np.maximum(np.zeros(act.shape),act - localavg)

        if save_act:
            pickle.dump(act, open(path_pickle, 'wb'))
    return act


def stft(x, fs, win_len, fps):
    # some pre calculations
    w = np.hanning(win_len)
    win_len_half = int(np.round(win_len / 2))
    if fs % fps != 0:
        raise ValueError("fs " + str(fs) + " is not divisable by fps " + str(fps))
    ana_hop = int(np.round(fs / fps))

    # pad the audio to center the windows and to avoid problems at the end
    x = np.concatenate((np.zeros(win_len_half), np.array(x), np.zeros(win_len_half)), axis=0)
    num_of_frames = int(np.floor((len(x) - win_len) / ana_hop + 1))

    # spectrogram calculation
    spec = np.zeros((win_len_half + 1, num_of_frames), dtype=complex)
    for i in range(num_of_frames):
        xi = x[i * ana_hop: i * ana_hop + win_len]
        xiw = xi * w
        Xi = np.fft.rfft(xiw)
        spec[:, i] = Xi

    # physical axis in seconds and Hertz
    t = np.array(list(range(num_of_frames))) / fs
    f = np.array(list(range(win_len_half + 1))) / win_len * fs

    return spec, f, t
