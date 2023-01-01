import numpy as np
import os
import sys
import soundfile as sf
import argparse
import re
import json

script_dir = os.path.dirname(__file__)
pygmu_dir = os.path.join(script_dir, "..", "pygmu")
sys.path.append(pygmu_dir)
import pygmu as pg
import utils as ut



SAMPLES_DIR = "samples"
LOOP_FILE_RE = re.compile(".*loop.*", re.IGNORECASE)
BPM_RE = re.compile(r".*?(\d+)bpm")

def is_loop_file(filename):
	"""Return true if filename contains "loop" as a substring."""
	return LOOP_FILE_RE.match(filename) is not None


def find_loop_files(root_dir):
	"""Search in and below root_dir for fienames with "loop" as a substring."""
	loop_files = []
	for root, subdirs, files in os.walk(root_dir):
		for filename in files:
			if is_loop_file(filename):
				file_path = os.path.join(root, filename)
				loop_files += [file_path]
	return loop_files

def loop_file_bpm(filename):
	"""Extract the BPM of a file, based on "NNNbpm" in the filename"""
	m = BPM_RE.match(filename)
	if m is None:
		return 0           # unknown BPM
	else:
		return m[1]

def collect_loop_file_details(loop_dict, loop_filename):
	"""Gather frame rate, channel count, duration and bpm for loop file"""
	info = sf.info(loop_filename)
	bpm = loop_file_bpm(loop_filename)
	loop_dict[loop_filename] = {
	  'frame_rate': info.samplerate,
	  'channel_count': info.channels,
	  'duration_s': info.duration,
	  'bpm': bpm}

def build_loop_file_dict():
	"""
	grovel over the samples directory to find filenames with "loop" as a substring.
	Print filename, beats per minute, sampling rate, # of channels and duration for
	inclusion as the SOURCE_LIBRARY dict.
	"""
	loop_filenames = find_loop_files(SAMPLES_DIR)
	loop_dict = {}
	for loop_filename in loop_filenames:
		collect_loop_file_details(loop_dict, loop_filename)
	return loop_dict

def assay():
	loop_dict = build_loop_file_dict()
	# pretty print the loop dict
	print(json.dumps(loop_dict, indent=4))


def process(args):
	if (args.assay):
		assay()

# =============================================================================
# Top level starts here

parser = argparse.ArgumentParser(prog="wip_RD05", description="Percussion Madness")
parser.add_argument('-a', '--assay', action='store_true', help='Search for sound samples')
parser.add_argument('-v', '--verbose', action='store_true')

args = parser.parse_args()
process(args)
