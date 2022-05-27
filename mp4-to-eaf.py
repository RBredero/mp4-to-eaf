##Converts .mp4 files to concatenated .wav and creates .EAF annotation file ##
##Version 2022-05-26##
##by Robin Bredero, adapted from scripts written by Kelsey C. Neely (https://github.com/kcneely) ##

##Descritption: This script takes uses .mp4 audio files as input (e.g., audio downloaded from WhatsApp) and, using the open-source software ffmpeg, converts these to a .wav file in which all input files are concatenated. Additionally, an .EAF file is created where each of the .mp4 files is a segment with the file name as corresponding annotation. The .EAF file can be used as a basis for further annotation of the .wav file. Note: this script mainly differs from the process-session.py and create-eaf.py scripts written by K. C. Neely (on which this script is based) in that it uses the original file names of the .mp4 files as annotations, rather than an automatically generated date + 24-hour time indication.

##Step 1: make sure you have python and ffmpeg installed, and save a back-up copy of the session files in case something goes wrong!
##Step 2: create a folder with as content this .py file, the programme ffmpeg.exe (can be downloaded for free at https://ffmpeg.org), and the .mp4 files that are to be converted.  
##Step 3: run this script by double clicking on it
##Step 4: check the concatenated file "Success.wav" to make sure the process was actually successful
##Step 4: If the script has worked, a .wav file titled "Success.wav" and an .eaf file titled "Success.eaf" will appear in the folder. Open the .wav file in an audio programme of choice and the .eaf file in ELAN to check that they work. The first time you open the .eaf file, you will need to indicate the name of the generated .wav file.
##Step 5: rename the files Success.wav and Success.eaf to match your project's filenaming conventions

import glob
import os
from datetime import datetime
import subprocess
import wave
import contextlib

##call ffmpeg to reencode individual mp4 files to wav files##
files = glob.glob('*.mp4')
for file in files:
    name = ''.join(file.split('.')[:-1])
    output = '{}.wav'.format(name)
    reencode = 'ffmpeg -i {} {}'.format(file, output)
    subprocess.call(reencode)

##create file listing##
names = [os.path.basename(x) for x in glob.glob('*.wav')]
names = map(lambda x: 'file \'' + x + '\'\n', names)
with open('output.txt', "w") as a:
    a.writelines(names)

##call ffmpeg to concatenate multiple wav to single wav##
filelist = 'output.txt'
output = 'Success.wav'
concatenate = 'ffmpeg -f concat -safe 0 -i {} {}'.format(filelist, output)
subprocess.call(concatenate)

#Set counters for time slot IDs and annotation IDs in .eaf file
annotation_index = 1
time_index = 2
time_value = 0

#Open .eaf (XML) file and define sections
with open('Success.eaf', "w") as a:
    header = '<?xml version="1.0" encoding="UTF-8"?>' + '\n' + '<ANNOTATION_DOCUMENT AUTHOR="" DATE="" FORMAT="3.0" VERSION="3.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://www.mpi.nl/tools/elan/EAFv3.0.xsd">' + '\n' + '\t' + '<HEADER MEDIA_FILE="" TIME_UNITS="milliseconds">' + '\n' + '\t \t' + '<MEDIA_DESCRIPTOR MEDIA_URL="file:///[FilePathAndName]" MIME_TYPE="audio/x-wav" RELATIVE_MEDIA_URL="./Success.wav"/>' + '\n' + '\t \t' + '<PROPERTY NAME="URN">urn:nl-mpi-tools-elan-eaf:8b09aae8-a8b8-4e21-8c96-14316c8e908a</PROPERTY>' + '\n' + '\t \t' + '<PROPERTY NAME="lastUsedAnnotationId">1</PROPERTY>' + '\n' + '\t' + '</HEADER>' + '\n' + '\t' + '<TIME_ORDER>' + '\n' + '\t \t' + '<TIME_SLOT TIME_SLOT_ID="ts1" TIME_VALUE="0"/>'
    
    middle = '\t' + '</TIME_ORDER>' + '\n' + '\t' + '<TIER LINGUISTIC_TYPE_REF="Text" TIER_ID="Original_Time_Stamps">' + '\n'
    
    footer = '\t' + '</TIER>' + '\n' + '\t' + '<LINGUISTIC_TYPE GRAPHIC_REFERENCES="false" LINGUISTIC_TYPE_ID="Text" TIME_ALIGNABLE="true"/>' + '\n' + '</ANNOTATION_DOCUMENT>'

#Write XML header and the opening tags for the time order portion of the .eaf file
    a.write(header)
    a.write('\n')

#Loop through files to get clip durations, convert times to ms, and write time slot IDs with time values
    files = glob.glob('*.wav')
    for file in files:
        file_name = os.path.basename(file)
        try:
            with contextlib.closing(wave.open(file_name,'r')) as f:
                frames = f.getnframes()
                rate = f.getframerate()
                duration = frames / float(rate)
                duration = str(duration)
                duration = float(duration)
                duration = int(duration * 1000)
                time_value = time_value + duration
                a.write('\t \t' + '<TIME_SLOT TIME_SLOT_ID="ts{}" TIME_VALUE="{}"/>'.format(time_index, time_value) + '\n')
                time_index = time_index + 1
        except:
            pass

#Write closing tags for time order portion and opening tags for annotation portion of .eaf file
    a.write(middle)

#Reset time slot ID to 1 and loop through files to generate annotations identical to the file name of the corresponding .wav clips
    time_index = 1
    for file in files:
        file_name = os.path.basename(file[:len(file)-4])
        try:
            annotation_value = file_name
            a.write('\t \t' + '<ANNOTATION>' + '\n' + '\t \t \t' + '<ALIGNABLE_ANNOTATION ANNOTATION_ID="{}" TIME_SLOT_REF1="ts{}" TIME_SLOT_REF2="ts{}">'.format(annotation_index, time_index, time_index + 1) + '\n' + '\t \t \t \t'+ '<ANNOTATION_VALUE>{}</ANNOTATION_VALUE>'.format(annotation_value) + '\n' + '\t \t \t' + '</ALIGNABLE_ANNOTATION>' + '\n' + '\t \t' + '</ANNOTATION>' + '\n')
            annotation_index = annotation_index + 1
            time_index = time_index + 1
        except:
            pass

#Write closing tags of annotation portion and footer of .eaf file
    a.write(footer)

##delete all generated .wav files in the folder except for the concatenated "master" file (assumes the file names are longer than 7 characters)##
files = glob.glob('*.wav')
for file in files:
    name = os.path.basename(file)
    if len(name)>15:
        os.remove(file)

##delete all generated .txt files in the folder ##
files = glob.glob('*.txt')
for file in files:
    name = os.path.basename(file)
    os.remove(name)


