![](img/Chordify.png) ![](img/tagtraum_industries.png) ![](img/AudioLabs.png)

# Chordify TapCorrect
This repository contains supplemental material for the paper "Towards Automatically Correcting Tapped Beat Annotations for Music Recordings" by Jonathan Driedger, Hendrik Schreiber, W. Bas de Haas, and Meinard Müller, presented at ISMIR 2019 in Delft, the Netherlands.

## Abstract
A common method to create beat annotations for music recordings is to let a human annotator tap along to them.
However, this method is problematic due to the limited human ability to temporally align taps with audio cues for beats accurately.
In order to create accurate beat annotations, it is therefore typically necessary to manually correct the recorded taps in a subsequent step, which is a cumbersome task.
In this work we aim to automate this correction step by "snapping" the taps to close-by audio cues---a strategy that is often used by beat tracking algorithms to refine their beat estimates.
The main contributions of this paper can be summarized as follows.
First, we formalize the automated correction procedure mathematically.
Second, we introduce a novel visualization method that serves as a tool to analyze the results of the correction procedure for potential errors. 
Third, we present a new dataset consisting of beat annotations for 101 music recordings.
Fourth, we use this dataset to perform a listening experiment as well as a quantitative study to show the effectiveness of our snapping procedure.

## TapCorrect Procedure
The folder `python` contains our implementation of the automatic trap correction procedure as described in the paper. The file `__main__.py` includes an example of how to execute the precedure.

## TapCorrect Dataset
The folder `dataset` contains the original taps, the automatically corrected taps, as well as the fully corrected taps, as well as metadata and YouTube links to all 101 music recordings used in the paper. Annotations are provided in both csv as well as jams format.
In the `csv` subfolder, you find one folder per item. Each folder then contains four csv-files:

* `00-meta.csv` conatining information about artist, title, track duration, and YouTube links.
* `01-original_taps.csv` containing a list of taps as created by the human annotator. Taps are given in the form `timestamp,"beat_count"`.
* `02-automatically_corrected_taps.csv` containing a list of taps automatically corrected by our proposed correction procedure.
* `03-fully_corrected_taps.csv` containing a list of manually corrected taps.

The `jams` subfolder contains 101 jams files (https://github.com/marl/jams). Each file contains the meta data as well as the three annotations listed above.

## Listening Experiment
The folder `listening_experiment` contains a spreadsheed with the detailed responses of our listening experiment's participants.