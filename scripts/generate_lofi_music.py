import math
import os
import random
import struct
import subprocess
import wave
import numpy as np

SAMPLE_RATE = 44100
DURATION = 30  # seconds
FFMPEG_BIN = "ffmpeg"
ARTIFACTS_DIR = "/config/.gemini/antigravity/brain/e2ff3a8c-2002-4bfe-b0a1-5d6523e32692"

def note_freq(name):
    notes = {'C4': 261.63, 'D4': 293.66, 'E4': 329.63, 'F4': 349.23, 'G4': 392.00, 'A4': 440.00, 'B4': 493.88,
             'C5': 523.25, 'D5': 587.33, 'E5': 659.25, 'F5': 698.46, 'G5': 783.99, 'A5': 880.00, 'B5': 987.77}
    return notes.get(name, 440.0)

def generate_lofi_track(filename="scripts/lofi_music.wav"):
    total_samples = int(SAMPLE_RATE * DURATION)
    t = np.linspace(0, DURATION, total_samples, endpoint=False)
    
    # 1. Warm Lo-Fi Chords (Cmaj7 -> Am7 -> Dm7 -> G7)
    chords = [
        ['C4', 'E4', 'G4', 'B4'],  # Cmaj7
        ['A4', 'C5', 'E5', 'G5'],  # Am7
        ['D4', 'F4', 'A4', 'C5'],  # Dm7
        ['G4', 'B4', 'D5', 'F5']   # G7
    ]
    
    chord_duration = 2.0  # seconds per chord
    music_signal = np.zeros(total_samples)
    
    for i in range(total_samples):
        time_sec = t[i]
        chord_idx = int(time_sec / chord_duration) % len(chords)
        current_chord = chords[chord_idx]
        
        # Soft tremolo envelope
        tremolo = 0.85 + 0.15 * math.sin(2 * math.pi * 5 * time_sec)
        
        chord_val = 0
        for note in current_chord:
            freq = note_freq(note)
            # Soft electric piano / warm synth tone (sine + gentle 2nd harmonic)
            val = math.sin(2 * math.pi * freq * time_sec) * 0.7 + math.sin(2 * math.pi * freq * 2 * time_sec) * 0.3
            chord_val += val
            
        chord_val = (chord_val / len(current_chord)) * tremolo
        music_signal[i] = chord_val

    # 2. Upbeat Lo-Fi Drum Beat (BPM 85)
    bpm = 85
    beat_sec = 60.0 / bpm
    drums_signal = np.zeros(total_samples)
    
    for i in range(total_samples):
        time_sec = t[i]
        beat_num = (time_sec / beat_sec) % 4
        beat_phase = (time_sec % beat_sec) / beat_sec
        
        # Kick on beat 0 and 2.5
        if (beat_num < 0.25) or (2.4 < beat_num < 2.65):
            kick_freq = 120 * math.exp(-beat_phase * 15)
            drums_signal[i] += math.sin(2 * math.pi * kick_freq * beat_phase) * math.exp(-beat_phase * 12) * 1.2
            
        # Snare/Clap on beat 1 and 3
        if (1.0 <= beat_num < 1.3) or (3.0 <= beat_num < 3.3):
            snare_phase = (time_sec % (beat_sec)) / beat_sec
            noise = (random.random() * 2 - 1)
            tone = math.sin(2 * math.pi * 180 * snare_phase) * 0.4
            drums_signal[i] += (noise * 0.6 + tone) * math.exp(-snare_phase * 15) * 0.8
            
        # Hi-hat on every 0.5 beat (8th notes)
        sub_beat = (time_sec / (beat_sec / 2)) % 1
        if sub_beat < 0.2:
            hat_noise = (random.random() * 2 - 1) * math.exp(-sub_beat * 35) * 0.25
            drums_signal[i] += hat_noise

    # 3. Subtle Vinyl Crackle Texture
    crackle = (np.random.rand(total_samples) * 2 - 1) * 0.02
    
    # 4. Master Mix
    mixed = music_signal * 0.45 + drums_signal * 0.5 + crackle
    max_val = np.max(np.abs(mixed))
    if max_val > 0:
        mixed = mixed / max_val * 0.85
        
    audio_int16 = (mixed * 32767).astype(np.int16)
    
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(audio_int16.tobytes())
        
    print(f"Generated upbeat lo-fi audio track: {filename}")
    return filename

def merge_video_audio(video_file, audio_file, output_mp4, output_webm):
    cmd_mp4 = [
        FFMPEG_BIN, "-y",
        "-i", video_file,
        "-i", audio_file,
        "-c:v", "libx264",
        "-c:a", "aac",
        "-shortest",
        output_mp4
    ]
    cmd_webm = [
        FFMPEG_BIN, "-y",
        "-i", video_file,
        "-i", audio_file,
        "-c:v", "copy",
        "-c:a", "libopus",
        "-shortest",
        output_webm
    ]
    
    print("Combining video and lo-fi music with FFmpeg...")
    subprocess.run(cmd_mp4, check=True)
    subprocess.run(cmd_webm, check=True)
    print("Successfully produced final demo videos with upbeat lo-fi music!")

if __name__ == "__main__":
    audio_path = generate_lofi_track()
    input_video = os.path.join(ARTIFACTS_DIR, "demo_video.webm")
    output_mp4 = os.path.join(ARTIFACTS_DIR, "demo_video_lofi.mp4")
    output_webm = os.path.join(ARTIFACTS_DIR, "demo_video_lofi.webm")
    merge_video_audio(input_video, audio_path, output_mp4, output_webm)
