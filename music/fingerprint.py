from typing import List
import numpy as np
import librosa as lr
from types import SimpleNamespace

audio_config = SimpleNamespace(
    base_path="assets/audio",
    sr=44100,
    mono=True,
    block_size=50,  # in ms
    block_ranges=[0, 1, 40, 80, 120, 160, 200],
    hash_bit_length=4,
)


class FingerprintPipeline:
    def __init__(self):
        pass

    def read_audio(self, file_name, file_path):
        audio_content, _ = lr.load(file_path + "/" + file_name, sr=audio_config.sr)
        block_count = int(
            len(audio_content) * (1000 / 50) / audio_config.sr
        )  # as 1000ms -> 1sec
        per_block_length = audio_config.sr * audio_config.block_size / 1000
        blocks = []

        for idx in range(block_count):
            start_idx = int(per_block_length * idx)
            end_idx = int(per_block_length * (idx + 1))
            blocks.append(audio_content[start_idx:end_idx])

        return blocks

    def fourier_transform(self, audio_blocks):
        dft_transformed = []
        dft_transformed_avg = []
        for block in audio_blocks:
            _fft_res_arr = np.abs(np.fft.fft(block))
            dft_transformed.append(_fft_res_arr)

            block_avg_val = (sum(_fft_res_arr) / len(_fft_res_arr)) * 1e20
            dft_transformed_avg.append(block_avg_val)

        return dft_transformed, dft_transformed_avg

    def complex_eval(self, complex_matrix):
        eval_arr = []
        for cmplex_arr in complex_matrix:
            tmp_array = []
            for sv in cmplex_arr:
                sv_bar = complex(sv.real, -sv.imag)
                tmp_array.append((sv * sv_bar).real)
                tmp_array.sort()
            eval_arr.append(tmp_array)

        return eval_arr

    def get_range_max(self, audio_blocks):
        positive_range = audio_config.block_ranges

        prv_matrix = []

        for ab_idx, audio_block in enumerate(audio_blocks):
            # creating an array with length 12 and all element filled with -1
            positive_range_values = [-1] * len(positive_range)
            for sv in audio_block:
                for idx, pr in enumerate(positive_range):
                    if (idx + 1) < len(positive_range):
                        min_lim_for_sv = positive_range[idx + 1]
                    else:
                        # a random maximum range to allow 250 to infinity in the last container.
                        min_lim_for_sv = 1e9
                    if (sv > pr) and (sv < min_lim_for_sv):
                        if positive_range_values[idx] < pr:
                            positive_range_values[idx] = sv

            prv_matrix.append(positive_range_values)
        return prv_matrix

    def hash_function(self, audio_blocks):
        pos_r = [0, 1, 40, 80, 120, 160, 200]
        bit_length = audio_config.hash_bit_length

        def division_size(r_min, r_max):
            return (r_max - r_min) / (2**bit_length)

        hashed_vals = []

        for s_block in audio_blocks:
            blck_hashes = ["0"] * len(pos_r)
            for sv in s_block:
                for idx, rng_lr in enumerate(pos_r):
                    if (idx + 1) < len(pos_r):
                        min_lim_for_sv = pos_r[idx + 1]
                    else:
                        # a random maximum range to allow 250 to infinity in the last container.
                        min_lim_for_sv = 1000
                    if (sv >= rng_lr) and (sv < min_lim_for_sv):
                        b_h = (sv - rng_lr) / division_size(rng_lr, min_lim_for_sv)
                        b_h = hex(int(b_h))
                        blck_hashes[idx] = b_h[2:]
            hashed_vals.append(blck_hashes)
        return hashed_vals

    def fingerprint(self, file_name, file_path=audio_config.base_path):
        audio_blocks = self.read_audio(file_name=file_name, file_path=file_path)
        audio_blocks, fingerprints = self.fourier_transform(audio_blocks=audio_blocks)
        # fingerprints = self.get_range_max(audio_blocks)
        # hashes = self.hash_function(fingerprints)

        return audio_blocks, fingerprints

    def hash_difference(self, hash_1: List[int], hash_2: List[int]):
        data_len = len(hash_1)
        h1 = sum(hash_1) / data_len
        h2 = sum(hash_2[:data_len]) / data_len

        return h1 - h2
