#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed 15 Jun 2022 02:56:09 PM EDT

@author: jdwood
"""

import argparse, os

DEFAULT_DIR = '/home/jdwood/Documents/Work/WA/Conversion/Doug_Schreiber/'
TIMING_DIR = 'COV_NT_timing'
AUDIO_DIR = 'COV_Audio'

class DirectoryScannerError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class DirectoryScanner:
    def __init__(self, directory):
        self.directory = directory
        self.files = []

    def scan(self):
        try:
            for filename in os.listdir(self.directory):
                filepath = os.path.join(self.directory, filename)
                if os.path.isfile(filepath):
                    self.files.append(filepath)
        except FileNotFoundError:
            raise DirectoryScannerError(f"Error: Directory '{self.directory}' not found.")
        except PermissionError:
            raise DirectoryScannerError(f"Error: Permission denied for directory '{self.directory}'.")

    def get_files(self):
        return self.files

class TimingDataParser:
    def __init__(self, file_path):
        """
        Initialize the TimingDataParser with a file path.

        :param file_path: The path to the timing data file.
        """
        self.file_path = file_path

class TimingDataParser:
    def __init__(self, file_path):
        """
        Initialize the TimingDataParser with a file path.

        :param file_path: The path to the timing data file.
        """
        self.file_path = file_path

    def parse_timing_data(self):
        """
        Parse the timing data from the file and extract the start and end times for each verse.

        :return: A dictionary with verse numbers as keys and tuples of start and end times as values.
        """
        timing_data = {}
        current_verse = None
        start_time = None
        with open(self.file_path, 'r') as file:
            for line in file:
                parts = line.strip().split()
                if len(parts) == 2: # Two parts means book metadata
                    tag, value = parts # USFM tag and its value
                    tag = tag.strip("\\")
                    match tag:
                        case "id":
                            self.id = value
                        case "c":
                            self.chapter = value
                    
                if len(parts) == 3: # Three part line means timing data
                    ftime, etime, verse = parts
                    verse_number = ""
                    verse_part = ""
                    for char in range(len(verse)):
                        if verse[char].isdigit():
                            verse_number = verse_number + str(verse[char])
                        elif verse[char].isalpha():
                            verse_part = verse[char]
                    if verse_number!= current_verse:
                        if current_verse is None:
                            current_verse = verse_number
                            start_time = float(ftime)
                        elif current_verse is not None:
                            timing_data[current_verse] = (start_time, float(ftime))
                            current_verse = verse_number
                        start_time = float(ftime)
                    else:
                        end_time = float(etime)
                    timing_data[current_verse] = (start_time, float(etime))
        return timing_data

# Example usage:

ap = argparse.ArgumentParser(description='Make TR project from a directory of MP3 files and a directory of timing files')
ap.add_argument('input_file1', type=str, help='Directory containing timing files')
ap.add_argument('input_file2', type=str, help='Directory containing MP3 files')
ap.add_argument('-o', '--output_file', type=str, nargs='?', help='Directory to receive the project')
ap.add_argument('-v', '--verbose', action='store_true', help='verbose mode')
args = ap.parse_args()

print(f"We'll be getting our timing files from {args.input_file1}")
print(f"The MP3 files are in {args.input_file2}")
if args.verbose:
    print('Verbose mode enabled')
if args.output_file is None:
    print("We'll be putting the output in this directory, since a destination was not provided. This will be a new folder with the correct name.")

scanner = DirectoryScanner(DEFAULT_DIR+TIMING_DIR)
try:
    scanner.scan()
    files = scanner.get_files()
    print(files)
    print('==================')
#    for file in files:
    print('Trying to get timing data from '+files[0])
    timing_data = TimingDataParser(files[0])
    td = timing_data.parse_timing_data()
    print(f"Book: {timing_data.id}")
    print(f"Chapter: {timing_data.chapter}")
    print(td)
    print('++++++++++++++++++++')
except DirectoryScannerError as e:
    print(e.message)