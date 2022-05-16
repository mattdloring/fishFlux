import os

from pathlib import Path


class ParentFinder:
    def __init__(self, some_base_directory):
        self.baseDir = some_base_directory

        self.fish = []
        self.stimuli = None

        self.parentSearch()

    def parentSearch(self):
        with os.scandir(self.baseDir) as entries:
            for entry in entries:
                if entry.is_dir():
                    self.fileSubmarine(entry.path)
                if ".hdf" in entry.name:
                    self.stimulipath = entry.path

    def fileSubmarine(self, baseDir):
        # recursively enter folders to find behavior logs
        with os.scandir(baseDir) as entries:
            for entry in entries:
                if "behavior_log" in entry.name:
                    self.fish.append(Path(entry.path).parents[0])
                elif Path(entry.path).is_dir():
                    self.fileSubmarine(entry.path)
