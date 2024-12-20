# Make TR

This program takes two folders as arguments.

The first folder contains `.txt` files, one for each chapter of each Bible book concerned. Each book is named like: `C01-01-MAT-01-timing.txt` The `01` right before `MAT` indicates book #1, and the `01` behind it indicates chapter 1.
It has a USFM heading that includes the book `\id` tag and the `\c` tag for the chapter number. It's possible that these files were generated by [Aeneas](https://github.com/readbeyond/aeneas).
There follows a long line of timings. These timings are of the format `0.000    3.240   1a`. The first number is the beginning of the slice, and the second number is the end, in seconds. The number at the end indicates the verse, and an alphabetic component indicates that the verse has been split into more than one slice.

The second folder contains folders. There is one folder for each concerned book. The folders are named like `01Matthew`, where `01` should match the book # above. Inside each of these folders is a collection of `.mp3` files, one for each chapter of the book. The .mp3 files are named like `ULB-Matthew-01.mp3`, where ULB is the identifier of the source, Matthew is the local name of the book, and `01` indicates the chapter.

The program reads the timing `.txt` files in an arbitrary order. For each text file it tries to locate an appropriate `.mp3` file (same book, same chapter). If it finds that file, it passes the file to [ffmpeg](https://github.com/FFmpeg/FFmpeg) which will using the timing numbers to split the `.mp3` file into `.mp3` files, one for each verse. These `.mp3` files will be written into a directory that is either specified, or located in the working directory as a subdirectory.

The `.mp3` files that are written will be in a directory structure as follows:
```
en
└── reg
    ├── mat
    │   ├── 01
    │   │   ├── en_reg_b41_mat_c01_v01_t01.mp3
```
This assumes that the language code provided is `en` (English).

Note that the actual book number for Matthew is 41, rather than 1. This is because the USFM code for Matthew implies the existence of the Old Testament. (I haven't heard the explanation of what happened to book 40.)

This folder structure should be able to be copied to the [BTT-Recorder](https://github.com/Bible-Translation-Tools/BTT-Recorder) folder on an Android device to be imported as a project file.

## Important Notes
Currently, the program assumes a New Testament project, and just adds 40 to every book number. This should be changed to make it more flexible for Old Testament projects.