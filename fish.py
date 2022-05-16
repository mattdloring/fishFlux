import os

import pandas as pd
import numpy as np
import numba as nb
import threading as tr

from fishFlux import stytra_boutfinding
from numba import jit


@jit(nopython=True)
def simplecum(arrvals):
    return np.cumsum(arrvals)

def simplechange(mylist):
    q = mylist[0].split('_')[1]

    times = []
    stim_ids = []
    for n, i in enumerate(mylist):

        splitup = i.split('_')

        if splitup[1] != q:
            times.append(splitup[0])
            stim_ids.append(splitup[1])

        q = splitup[1]
    return times, stim_ids


class Fish:
    def __init__(self, fish_path, stimuli):
        self.fishPath = fish_path
        self.stimuli = stimuli

        self.preload_metadataFromPath()
        self.preload_subPaths()

    def preload_metadataFromPath(self):
        strungPath = str(self.fishPath)
        strungPathList = strungPath.split('\\')
        self.rig_n = int(strungPathList[-2][-1])
        self.fish_n = int(strungPathList[-1])

    def preload_subPaths(self):
        with os.scandir(self.fishPath) as entries:
            for entry in entries:
                if "behavior_log" in entry.name:
                    self.behavior_log_path = entry.path
                elif "estimator_log" in entry.name:
                    self.estimator_log_path = entry.path
                elif "metadata.json" in entry.name:
                    self.metadata_raw_path = entry.path
                    try:
                        self.stytra_exp = stytra_boutfinding.StytraExp(self.metadata_raw_path)
                    except Exception as e:
                        print(f'failed to load stytra experiment {e}')
                elif "bouts.h5" in entry.name:
                    self.bouts_path = entry.path
                elif "dataframe.h5" in entry.name:
                    self.dataframe_path = entry.path
                else:
                    if entry.name.endswith('.txt'):
                        self.raw_stims_path = entry.path

    def load_behavior(self):
        try:
            self.behavior_log = pd.read_csv(self.behavior_log_path, sep=';', dtype=np.float32)
        except Exception as e:
            print(f'exception reading behavior log {e}')

    def process_bouts(self):
        self.bouts_list, self.continuity = stytra_boutfinding.extract_bouts(self.stytra_exp)
        self.bouts = pd.concat(self.bouts_list, keys=np.arange(len(self.bouts_list)))

    def process_rawstim(self):

        with open(self.raw_stims_path) as file:
            contents = file.read()
        parsed = contents.split('\n')
        stimDetailList = parsed[1:]  # remove header
        self.times, self.stim_ids = simplechange(stimDetailList)

    def tr_loader(self):
        fxns = [self.process_rawstim, self.process_bouts, self.load_behavior]
        threads = [tr.Thread(target=f) for f in fxns]
        [t.start() for t in threads]
        [t.join() for t in threads]


    def straight_loader(self):
        self.process_rawstim()
        self.process_bouts()
        self.load_behavior()
