import numpy as np
import math

# This bit of boilerplate allows Python to find the pygmu library
import os
import sys
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import pygmu as pg
import utils as ut

from extent import Extent
from pyg_pe import PygPE

from music21 import converter, note, chord

class Note:
    def __init__(self, offset, duration, pitch, velocity=100):
        self._offset = offset
        self._duration = duration
        self._pitch = pitch
        self._velocity = velocity
        self._extent = self.compute_extent()
    def __repr__(self):
        return f"""<Note {self.__hash__()}: offset={str(self._offset)}, duration={str(self._duration)}, pitch={ut.midi_to_note(self._pitch)}, velocity={str(self._velocity)}>"""
    def offset(self, tempo = 120, frame_rate = 48000):
        return int(self._offset * 60 / tempo * frame_rate)
    def duration(self, tempo = 120, frame_rate = 48000, rel_secs = 0):
        return int(((self._duration * 60 / tempo) + rel_secs)  * frame_rate)
    def extent(self, tempo = 120, frame_rate = 48000, rel_secs = 0):
        self.compute_extent(tempo, frame_rate, rel_secs)
        return self._extent
    def compute_extent(self, tempo = 120, frame_rate = 48000, rel_secs = 0):
        self._extent = pg.Extent(self.offset(tempo, frame_rate), (self.offset(tempo, frame_rate) + self.duration(tempo, frame_rate, rel_secs)))
        return self._extent
    def interpolation(self, native_pitch = 60):
        steps = self._pitch - native_pitch
        return math.pow(2, steps / 12)

def get_notes_from_midi(midi_path):
    # Parse the MIDI file with music21
    midi_file = converter.parse(midi_path)
    
    notes = []
    for part in midi_file.parts:
        # Use .flat.notes to get a flattened list of Note and Chord objects
        for element in part.flat.notes:
            # Check if the element is a note.Note object
            if isinstance(element, note.Note):
                pyg_note = pg.Note(element.offset, element.duration.quarterLength, element.pitch.midi, element.volume.velocity)
                pyg_note.music21_note = element
                notes.append(pyg_note)
                print(pyg_note)
            # Check if the element is a chord.Chord object
            elif isinstance(element, chord.Chord):
                for pitch in element.pitches:
                    pyg_note = pg.Note(element.offset, element.duration.quarterLength, pitch.midi, element.volume.velocity)
                    pyg_note.music21_note = element
                    notes.append(pyg_note)
    return notes

class NotesPE(PygPE):
    """
    Use a list of notes to produce one or more cropped and pitch-adjusted PEs mixed together
    """

    def __init__(self, src_pe, note_list, tempo = 120, gain_factor = 0.24, native_pitch = 60, atk_secs = 0, rel_secs = 0):
        super(NotesPE, self).__init__()
        self._src_pe = src_pe
        self._note_list = note_list
        self._tempo = tempo
        self._gain_factor = gain_factor
        self._native_pitch = native_pitch
        self._atk_secs = atk_secs
        self._rel_secs = rel_secs
        self._extent = self.compute_extent()
        self.build_internal_pes()

    def build_internal_pes(self):
        """
        build PEs for each of the notes
        """
        for a_note in self._note_list:
            vol = self._gain_factor * (120 + ut.velocity_to_db(a_note._velocity)) / 120
            note_dur_frames = a_note.duration(self._tempo, self.frame_rate(), self._rel_secs)
            note_offset_frames = a_note.offset(self._tempo, self.frame_rate())
            fab_pe = pg.WarpSpeedPE(self._src_pe,a_note.interpolation(self._native_pitch)).crop(pg.Extent(0,note_dur_frames)).gain(vol).splice(int(self._atk_secs * self.frame_rate()),int(self._rel_secs * self.frame_rate())).time_shift(note_offset_frames)
            a_note.fab_pe = fab_pe

    def render(self, requested:Extent):
        dst_buf = np.zeros([self.channel_count(), requested.duration()], np.float32)
        fr = self.frame_rate()
        for a_note in self._note_list:
            relevant = requested.intersect(a_note.extent(self._tempo, fr, self._rel_secs))
            if relevant.is_empty():
                continue
            fab_pe = a_note.fab_pe
            dst_buf += fab_pe.render(requested)
        return dst_buf
    
    def extent(self):
        return self._extent

    def frame_rate(self):
        return self._src_pe.frame_rate()

    def channel_count(self):
        return self._src_pe.channel_count()

    def compute_extent(self):
        if len(self._note_list) == 0:
            return Extent()
        else:
            # start with the extent of the first note, extend it by taking the
            # union with each following note's extent.
            extent = self._note_list[0].extent(self._tempo, self.frame_rate())
            for note in self._note_list[1:]:
                extent = extent.union(note.extent(self._tempo, self.frame_rate()))  # TODO extend by rel_secs
            return extent
