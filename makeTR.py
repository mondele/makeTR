#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed 15 Jun 2022 02:56:09 PM EDT

@author: jdwood
"""

import argparse, os
import subprocess, regex

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
                elif os.path.isdir(filepath):
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

    def parse_timing_data(self):
        """
        Parse the timing data from the file and extract the start and end times for each verse.

        :return: A dictionary with verse numbers as keys and tuples of start and end times as values.
        """
        timing_data = {}
        current_verse = None
        start_time = None
        with open(self.file_path, 'r') as file:
            try:
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
            except Exception as e:
                print(f"Error parsing timing data: {e}")
        return timing_data

class ProjectFolder:
    def __init__(self, file_path):
        """
        Initialize the ProjectFolder with a file path.

        :param file_path: Where the project will be written
        """
        self.file_path = file_path
    
    def ProjectFolderSetup(self):
        # BTTR project is set up in this way:
        #   language_code/project_type/book_code/chapter
        # so e.g.
        #   zh/ulb/mat/01
        # or
        #   en/reg/phi/04

        print(f"\nProject will go in {self.file_path}")

        if not os.path.exists(self.file_path):
            os.makedirs(self.file_path)

def find_file_name(file_names, number):
    pattern = r'(?:^|-)(\d\d)'
    for file_name in file_names:
        match = regex.search(pattern, os.path.basename(file_name))
        if match and match.group(1).isnumeric:
            return file_name
    return None
        

# Establish arguments
ap = argparse.ArgumentParser(description='Make TR project from a directory of MP3 files and a directory of timing files')
ap.add_argument('-l', '--language_code', type=str, help='Language code for project')
ap.add_argument('-t', '--timing_file', type=str, help='Directory containing timing files')
ap.add_argument('-m', '--mp3_file', type=str, help='Directory containing MP3 files')
ap.add_argument('-o', '--output_file', type=str, nargs='?', help='Directory to receive the project')
ap.add_argument('-v', '--verbose', action='store_true', help='verbose mode')
args = ap.parse_args()

timing_dir = args.timing_file
mp3_dir = args.mp3_file
output_dir = args.output_file
print(f"We'll be getting our timing files from {timing_dir}")
print(f"The MP3 files are in {mp3_dir}")
if args.verbose:
    print('Verbose mode enabled')
if output_dir is None:
    output_dir = os.getcwd()
    print(f"We'll be putting the output in {output_dir}, since a destination was not provided. This will be a new folder with the correct name.")

language_code = args.language_code

# Example usage:

scanner = DirectoryScanner(DEFAULT_DIR+TIMING_DIR)
try:
    scanner.scan()
    files = scanner.get_files()
    for file in files:
        timing_data = TimingDataParser(file)
        td = timing_data.parse_timing_data()

        file_path = file
        base_filename = os.path.splitext(os.path.basename(file_path))[0]
        book_number = base_filename.split("-")[1]

        # book_number can be used to find the correct mp3 file later

        print(file)
        print(f"Book Number: {book_number}")
        print(f"Book: {timing_data.id}")
        print(f"Chapter: {timing_data.chapter}")
        print(f"There are {len(td)} verses in this chapter")

        targetPath = f"{output_dir}/{language_code}/reg/{timing_data.id}/{timing_data.chapter.zfill(2)}"
        targetFolder = ProjectFolder(targetPath)

        # find the audio for this book and chapter
        dir_scanner = DirectoryScanner(mp3_dir)
        dir_scanner.scan()
        directories = dir_scanner.get_files()
        mp3_folder = find_file_name(directories, book_number)

        # found the book, now find the chapter.
        audio_scanner = DirectoryScanner(mp3_folder)
        audio_scanner.scan()
        audio_files = audio_scanner.get_files()
        print(f"We'll try to get chapter {timing_data.chapter}")
        audio_file = find_file_name(audio_files, timing_data.chapter)
        print(audio_file)

        tempVar = targetFolder.ProjectFolderSetup()

        for verse in td:
            start_time, end_time = td[verse]
            verse = verse.zfill(2)
            # Sample audio filename: zha-x-chineseoralversion_reg_b41_mat_c01_v01_t01.wav
            output_file = f"{targetPath}/{language_code}_reg_b{book_number}_{timing_data.id}_c{timing_data.chapter.zfill(2)}_v{verse.zfill(2)}_t01.wav"

            ffmpeg_command = ['ffmpeg', '-i', audio_file, '-ss', str(start_time), '-to', str(end_time), '-c', 'copy', '-n', output_file]
            subprocess.run(ffmpeg_command)

# ffmpeg -i input.mp3 -ss 00:01:23.456 -t 00:00:10.500 -c copy output.wav

except DirectoryScannerError as e:
    print(e.message)