import argparse
import json
import numpy as np
import os
import random
import re
import soundfile as sf
import sys

script_dir = os.path.dirname(__file__)
pygmu_dir = os.path.join(script_dir, "..", "pygmu")
sys.path.append(pygmu_dir)
import pygmu as pg
import utils as ut

"""
Find all sound files in the samples/ directory that have the word "loop" and
"bpm" in their filename.  From those files, extract the frame rate, channel
count and duration, saving all the info in a python dict structure.

"""

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
		return int(m[1])

def collect_loop_file_details(loop_dict, loop_filename):
	"""Gather frame rate, channel count, duration and bpm for loop file"""
	info = sf.info(loop_filename)
	bpm = loop_file_bpm(loop_filename)
	loop_dict[loop_filename] = {
	  'frame_rate': info.samplerate,
	  'channel_count': info.channels,
	  'duration_s': info.duration,
	  'beats_per_minute': bpm}

def build_loop_file_dict():
	"""
	grovel over the samples directory for filenames with "loop" as a substring.
	Collect filename, beats per minute, sampling rate, number of channels 
	and duration to build the a dictionary with an entry for each file.
	"""
	loop_filenames = find_loop_files(SAMPLES_DIR)
	loop_dict = {}
	for loop_filename in loop_filenames:
		collect_loop_file_details(loop_dict, loop_filename)
	return loop_dict

def print_dict(loop_dict):
	# pretty print the loop dict
	print(json.dumps(loop_dict, indent=4))


# =============================================================================
# Top level starts here

def top_level(args):
	loop_dict = build_loop_file_dict()
	if args.print or args.verbose:
		print_dict(loop_dict)
	if (args.seed):
		random.seed(args.seed)


parser = argparse.ArgumentParser(prog="wip_RD05", description="Percussion Madness")
parser.add_argument('-p', '--print', action='store_true', help='Print loop files (only)')
parser.add_argument('-s', '--seed', type=int, help='Set random seed')
parser.add_argument('-v', '--verbose', action='store_true')

args = parser.parse_args()
top_level(args)
