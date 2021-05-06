from tapcorrect import tapcorrection

if __name__ == '__main__':

    path_audio = "../data/2011_TashaYaar_TheCatTheBatAndThePenguine.wav"
    path_taps = "../data/2011_TashaYaar_TheCatTheBatAndThePenguine_taps_orig.csv"
    path_out = "../data/2011_TashaYaar_TheCatTheBatAndThePenguine_taps_corrected.csv"

    tapcorrection.correct_taps(path_taps, path_audio,
                               method_sequence_computation='dtw',
                               method_act_curve='madmom',
                               visualize=True,
                               write_results=True,
                               path_out=path_out,
                               save_actcurves=False)