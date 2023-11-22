root_path = "C:\Users\mahit\Desktop\recognized\audio"
# -*- coding: utf-8 -*-



import os
os.listdir(root_path)

import numpy as np
import matplotlib.pyplot as plt
plt.rcParams['figure.figsize'] = [8, 6]
plt.rcParams['figure.dpi'] = 140 # 200 e.g. is really fine, but slower
from scipy import fft, signal
import scipy
from scipy.io.wavfile import read

# Read the input WAV files
# Fs is the sampling frequency of the file
Fs, song = read(f"{root_path}/o0gxXmrl7Gy9UGzSYi9z__Protikkha (1).wav")

time_to_plot = np.arange(Fs * 1, Fs * 1.3, dtype=int)
plt.plot(time_to_plot, song[time_to_plot])
plt.title("Sound Signal Over Time")
plt.xlabel("Time Index")
plt.ylabel("Magnitude");

import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq
# Number of sample points
N = 600
# sample spacing
T = 1.0 / 800.0
x = np.linspace(0.0, N*T, N, endpoint=False)

# Create a signal comprised of 5 Hz wave and an 10 Hz wave
y = np.sin(5.0 * 2.0*np.pi*x) + 0.75*np.sin(10.0 * 2.0*np.pi*x)
yf = fft(y)
xf = fftfreq(N, T)[:N//2]

plt.subplot(1, 2, 1)
plt.plot(x, y)
plt.xlabel("Time (s)")
plt.subplot(1, 2, 2)
plt.plot(xf, 2.0/N * np.abs(yf[0:N//2]))
plt.grid()
plt.xlabel("Frequency (Hz)")
plt.xlim(0, 60)
plt.show()

y = np.sin(5.0 * 2.0*np.pi*x) + 0.75*np.sin(10.0 * 2.0*np.pi*x)

# Add Gaussian Noise to one of the signals
y_corrupted = y + np.random.normal(0, 2.5, len(y))

# Plot and perform the same FFT as before

plt.subplot(2, 2, 1)
plt.plot(x, y)
plt.xlabel("Time (s)")
plt.grid()
plt.subplot(2, 2, 3)
plt.plot(x, y_corrupted)
plt.xlabel("Time (s)")
plt.grid()

yf = fft(y)
xf = fftfreq(N, T)[:N//2]
plt.subplot(2, 2, 2)
plt.plot(xf, 2.0/N * np.abs(yf[0:N//2]))
plt.xlim(0, 60)
plt.xlabel("Frequency (Hz)")
plt.grid()

yf = fft(y_corrupted)
xf = fftfreq(N, T)[:N//2]
plt.subplot(2, 2, 4)
plt.plot(xf, 2.0/N * np.abs(yf[0:N//2]))
plt.xlim(0, 60)
plt.xlabel("Frequency (Hz)")
plt.grid()

N = len(song)
fft = scipy.fft.fft(song)
transform_y = 2.0 / N * np.abs(fft[0:N//2])

transform_x = scipy.fft.fftfreq(N, 1 / Fs)[:N//2]
plt.plot(transform_x, transform_y)
plt.xlabel("Frequency (Hz)");

transform_y.shape

all_peaks, props = signal.find_peaks(transform_y)


peaks, props = signal.find_peaks(transform_y, prominence=0, distance=10000)
n_peaks = 15

# Get the n_peaks largest peaks from the prominences
# This is an argpartition
# Useful explanation: https://kanoki.org/2020/01/14/find-k-smallest-and-largest-values-and-its-indices-in-a-numpy-array/
largest_peaks_indices = np.argpartition(props["prominences"], -n_peaks)[-n_peaks:]
largest_peaks = peaks[largest_peaks_indices]


plt.plot(transform_x, transform_y, label="Spectrum")
plt.scatter(transform_x[largest_peaks], transform_y[largest_peaks], color="r", zorder=10, label="Constrained Peaks")

plt.show()

# Some parameters
window_length_seconds = 3
window_length_samples = int(window_length_seconds * Fs)
window_length_samples += window_length_samples % 2

# Perform a short time fourier transform
# frequencies and times are references for plotting/analysis later
# the stft is a NxM matrix
frequencies, times, stft = signal.stft(
    song, Fs, nperseg=window_length_samples,
    nfft=window_length_samples, return_onesided=True
)

stft.shape

constellation_map = []

for time_idx, window in enumerate(stft.T):
    # Spectrum is by default complex.
    # We want real values only
    spectrum = abs(window)
    # Find peaks - these correspond to interesting features
    # Note the distance - want an even spread across the spectrum
    peaks, props = signal.find_peaks(spectrum, prominence=0, distance=200)

    # Only want the most prominent peaks
    # With a maximum of 5 per time slice
    n_peaks = 5
    # Get the n_peaks largest peaks from the prominences
    # This is an argpartition
    # Useful explanation: https://kanoki.org/2020/01/14/find-k-smallest-and-largest-values-and-its-indices-in-a-numpy-array/
    largest_peaks = np.argpartition(props["prominences"], -n_peaks)[-n_peaks:]
    for peak in peaks[largest_peaks]:
        frequency = frequencies[peak]
        constellation_map.append([time_idx, frequency])

# Transform [(x, y), ...] into ([x1, x2...], [y1, y2...]) for plotting using zip
plt.scatter(*zip(*constellation_map));

def create_constellation(audio, Fs):
    # Parameters
    window_length_seconds = 0.5
    window_length_samples = int(window_length_seconds * Fs)
    window_length_samples += window_length_samples % 2
    num_peaks = 15

    # Pad the song to divide evenly into windows
    amount_to_pad = window_length_samples - audio.size % window_length_samples

    song_input = np.pad(audio, (0, amount_to_pad))

    # Perform a short time fourier transform
    frequencies, times, stft = signal.stft(
        song_input, Fs, nperseg=window_length_samples, nfft=window_length_samples, return_onesided=True
    )

    constellation_map = []

    for time_idx, window in enumerate(stft.T):
        # Spectrum is by default complex.
        # We want real values only
        spectrum = abs(window)
        # Find peaks - these correspond to interesting features
        # Note the distance - want an even spread across the spectrum
        peaks, props = signal.find_peaks(spectrum, prominence=0, distance=200)

        # Only want the most prominent peaks
        # With a maximum of 15 per time slice
        n_peaks = min(num_peaks, len(peaks))
        # Get the n_peaks largest peaks from the prominences
        # This is an argpartition
        # Useful explanation: https://kanoki.org/2020/01/14/find-k-smallest-and-largest-values-and-its-indices-in-a-numpy-array/
        largest_peaks = np.argpartition(props["prominences"], -n_peaks)[-n_peaks:]
        for peak in peaks[largest_peaks]:
            frequency = frequencies[peak]
            constellation_map.append([time_idx, frequency])

    return constellation_map

constellation_map = create_constellation(song, Fs)

def create_hashes(constellation_map, song_id=None):
    hashes = {}
    # Use this for binning - 23_000 is slighlty higher than the maximum
    # frequency that can be stored in the .wav files, 22.05 kHz
    upper_frequency = 23_000
    frequency_bits = 10

    # Iterate the constellation
    for idx, (time, freq) in enumerate(constellation_map):
        # Iterate the next 100 pairs to produce the combinatorial hashes
        # When we produced the constellation before, it was sorted by time already
        # So this finds the next n points in time (though they might occur at the same time)
        for other_time, other_freq in constellation_map[idx : idx + 100]:
            diff = other_time - time
            # If the time difference between the pairs is too small or large
            # ignore this set of pairs
            if diff <= 1 or diff > 10:
                continue

            # Place the frequencies (in Hz) into a 1024 bins
            freq_binned = freq / upper_frequency * (2 ** frequency_bits)
            other_freq_binned = other_freq / upper_frequency * (2 ** frequency_bits)

            # Produce a 32 bit hash
            # Use bit shifting to move the bits to the correct location
            hash = int(freq_binned) | (int(other_freq_binned) << 10) | (int(diff) << 20)
            hashes[hash] = (time, song_id)
    return hashes

# Quickly investigate some of the hashes produced
hashes = create_hashes(constellation_map, 0)
for i, (hash, (time, _)) in enumerate(hashes.items()):
    if i > 10:
        break
    print(f"Hash {hash} occurred at {time}")

import glob
from typing import List, Dict, Tuple
from tqdm import tqdm
import pickle

songs = glob.glob(f'{root_path}/*.wav')

song_name_index = {}
database: Dict[int, List[Tuple[int, int]]] = {}

# Go through each song, using where they are alphabetically as an id
for index, filename in enumerate(tqdm(sorted(songs))):
    song_name_index[index] = filename
    # Read the song, create a constellation and hashes
    Fs, audio_input = read(filename)
    constellation = create_constellation(audio_input, Fs)
    hashes = create_hashes(constellation, index)

    # For each hash, append it to the list for this hash
    for hash, time_index_pair in hashes.items():
        if hash not in database:
            database[hash] = []
        database[hash].append(time_index_pair)
# Dump the database and list of songs as pickles
with open("database.pickle", 'wb') as db:
    pickle.dump(database, db, pickle.HIGHEST_PROTOCOL)
with open("song_index.pickle", 'wb') as songs:
    pickle.dump(song_name_index, songs, pickle.HIGHEST_PROTOCOL)

# Load the database
database = pickle.load(open('database.pickle', 'rb'))
song_name_index = pickle.load(open("song_index.pickle", "rb"))

# Load a short recording with some background noise
Fs, audio_input = read(f"{root_path}/recog/proti.wav")
# Create the constellation and hashes
constellation = create_constellation(audio_input, Fs)
hashes = create_hashes(constellation, None)

# For each hash in the song, check if there's a match in the database
# There could be multiple matching tracks, so for each match:
#   Incrememnt a counter for that song ID by one
matches_per_song = {}
for hash, (sample_time, _) in hashes.items():
    if hash in database:
        matching_occurences = database[hash]
        for source_time, song_id in matching_occurences:
            if song_id not in matches_per_song:
                matches_per_song[song_id] = 0
            matches_per_song[song_id] += 1

for song_id, num_matches in list(sorted(matches_per_song.items(), key=lambda x: x[1], reverse=True))[:10]:
    print(f"Song: {song_name_index[song_id]} - Matches: {num_matches}")

