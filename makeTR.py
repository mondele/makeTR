#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed 15 Jun 2022 02:56:09 PM EDT

@author: jdwood
"""

import argparse, os
import subprocess, regex
import unittest
from unittest.mock import patch, MagicMock
from your_module import DirectoryScanner, TimingDataParser, ProjectFolder

class TestDirectoryScanner(unittest.TestCase):
    def test_scan_directory(self):
        # Create a mock directory with some files
        mock_dir = MagicMock()
        mock_dir.listdir.return_value = ['file1.txt', 'file2.txt', 'dir1']

        # Create a DirectoryScanner instance
        scanner = DirectoryScanner(mock_dir)
        scanner.scan()

        # Assert that the files were scanned correctly
        self.assertEqual(scanner.get_files(), ['file1.txt', 'file2.txt', 'dir1'])

    def test_scan_directory_with_error(self):
        # Create a mock directory that raises an error
        mock_dir = MagicMock()
        mock_dir.listdir.side_effect = Exception('Mock error')

        # Create a DirectoryScanner instance
        scanner = DirectoryScanner(mock_dir)

        # Assert that the error is raised
        with self.assertRaises(Exception):
            scanner.scan()

class TestTimingDataParser(unittest.TestCase):
    def test_parse_timing_data(self):
        # Create a mock file with some timing data
        mock_file = MagicMock()
        mock_file.read.return_value ='some timing data'

        # Create a TimingDataParser instance
        parser = TimingDataParser(mock_file)
        timing_data = parser.parse_timing_data()

        # Assert that the timing data was parsed correctly
        self.assertIsInstance(timing_data, dict)

    def test_parse_timing_data_with_error(self):
        # Create a mock file that raises an error
        mock_file = MagicMock()
        mock_file.read.side_effect = Exception('Mock error')

        # Create a TimingDataParser instance
        parser = TimingDataParser(mock_file)

        # Assert that the error is raised
        with self.assertRaises(Exception):
            parser.parse_timing_data()

class TestProjectFolder(unittest.TestCase):
    def test_project_folder_setup(self):
        # Create a mock project folder
        mock_folder = MagicMock()

        # Create a ProjectFolder instance
        folder = ProjectFolder(mock_folder)
        folder.ProjectFolderSetup()

        # Assert that the project folder was set up correctly
        self.assertTrue(mock_folder.exists())

    def test_project_folder_setup_with_error(self):
        # Create a mock project folder that raises an error
        mock_folder = MagicMock()
        mock_folder.exists.side_effect = Exception('Mock error')

        # Create a ProjectFolder instance
        folder = ProjectFolder(mock_folder)

        # Assert that the error is raised
        with self.assertRaises(Exception):
            folder.ProjectFolderSetup()

if __name__ == '__main__':
    unittest.main()

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
        if args.verbose:
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
        
def main():
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
    if args.verbose:
        print('Verbose mode enabled')

    if args.verbose:
        print(f"We'll be getting our timing files from {timing_dir}")
        print(f"The MP3 files are in {mp3_dir}")
    if output_dir is None:
        output_dir = os.getcwd()
        print(f"We'll be putting the output in {output_dir}, since a destination was not provided. This will be a new folder with the correct name.")

    language_code = args.language_code.lower()

    scanner = DirectoryScanner(args.timing_file)
    try:
        scanner.scan()
        files = scanner.get_files()
        # files is a list of timing files
        for file in files:
            # We'll extract the book number, name, and chapter number from the filename of the timing file.
            base_filename = os.path.splitext(os.path.basename(file))[0]
            book_number, book_name, chapter_number = base_filename.split("-")[1:4]
            book_name = book_name.lower()
            # each book will have as many timing files as it has chapters.
            timing_data = TimingDataParser(file)
            # the parser will go through the file line by line to find out the timing for each verse in that chapter
            td = timing_data.parse_timing_data()
            # td is the parsed timing data for this particular chapter
            if book_name == timing_data.id.lower() and chapter_number == timing_data.chapter.zfill(2):
                print(f"Book name and chapter match from filename to metadata") if args.verbose else None
            else:
                print("The book name and / or chapter don't match from filename to metadata")
                print(f"Book name is {book_name} vs. {timing_data.id}")
                print(f"Chapter is {chapter_number} vs. {timing_data.chapter}")

            if args.verbose:
                print(file)
                print(f"Book Number: {book_number}")
                print(f"Book: {timing_data.id}")
                print(f"Chapter: {timing_data.chapter}")
                print(f"There are {len(td)} verses in this chapter")

            targetPath = f"{output_dir}/{language_code}/reg/{book_name}/{chapter_number}"
            targetFolder = ProjectFolder(targetPath)

            # find the audio for this book and chapter
            dir_scanner = DirectoryScanner(mp3_dir)
            dir_scanner.scan()
            directories = dir_scanner.get_files()

            for book_folder in directories:
                if os.path.basename(book_folder).startswith(str(book_number)):
                    book_number = str(int(book_number)+40)
                    chapter_files = os.listdir(book_folder)
                    for chapter_file in chapter_files:
                        chapter_filename = os.path.splitext(os.path.basename(chapter_file))[0]
                        if chapter_filename.endswith(f"-{chapter_number}"):
                            # match found
                            audio_file = f"{book_folder}/{chapter_file}"
                            tempVar = targetFolder.ProjectFolderSetup()

                            if audio_file is not None:
                                for verse in td:
                                    start_time, end_time = td[verse]
                                    verse = verse.zfill(2)
                                    # Sample audio filename: zha-x-chineseoralversion_reg_b41_mat_c01_v01_t01.wav

                                    output_file = f"{targetPath}/{language_code}_reg_b{book_number}_{book_name}_c{chapter_number}_v{verse}_t01.wav"
                                # print(f"Writing from {audio_file} to {output_file} for verse number {verse}")
                                    if not os.path.exists(output_file):
                                        if start_time < end_time:
                                            try:
                                                ffmpeg_command = ['ffmpeg', '-i', audio_file, '-ss', str(start_time), '-to', str(end_time), '-loglevel', 'panic', '-c', 'copy', '-n', output_file]
                                                result = subprocess.run(ffmpeg_command, capture_output=True)
                                                if result.returncode!=0:
                                                    print(f"Error executing ffmpeg command\n\t{ffmpeg_command}\n\t\t: {result.stderr.decode()}")
                                            except subprocess.CalledProcessError as e:
                                                print(f"Error executing ffmpeg command\n\t{ffmpeg_command}\n\t\t: {e}")
                                        else:
                                            print(f"Start time: {start_time} and end time: {end_time} do not increment properly.")
                                    else: print(f"{output_file} already exists.")
                            else:
                                print(f"Error: Could not find audio file for book {book_number} chapter {chapter_number}")

    # ffmpeg -i input.mp3 -ss 00:01:23.456 -t 00:00:10.500 -c copy output.wav

    except DirectoryScannerError as e:
        print(e.message)

if __name__ == '__main__':
    main()