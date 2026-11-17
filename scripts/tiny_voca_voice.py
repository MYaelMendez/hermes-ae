"""tiny-voca local voice layer — self-hosted TTS for æ agents.

ONNX Runtime path (no PyTorch needed). English only, voices F2/M2, 24 kHz.
Weights: /opt/data/tiny-voca-weights (model.onnx SHA256 verified).
"""
import os, sys, wave, hashlib, json
from pathlib import Path

ROOT = Path('/opt/data/tiny-voca-weights')
os.environ.setdefault('DIZIONE_DATA', str(ROOT / 'phonemizer'))
MODEL = ROOT / 'onnx' / 'model.onnx'
CONFIG = ROOT / 'config.json'
VOICES = {'F2': 0, 'M2': 1}
SR = 24000

try:
    import numpy as np
    import onnxruntime as ort
    import dizione
except ImportError as e:
    raise SystemExit(f'missing dependency: {e}')

_session = None


def session():
    global _session
    if _session is None:
        so = ort.SessionOptions()
        so.intra_op_num_threads = 4
        so.log_severity_level = 3
        _session = ort.InferenceSession(str(MODEL), so, providers=['CPUExecutionProvider'])
    return _session


def split_sentences(text, limit=300):
    import re
    parts = re.split(r'(?<=[.!?])\s+', text.strip())
    out = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        if p[-1] not in '.!?':
            p += '.'
        while len(p) > limit:
            cut = p.rfind(' ', 0, limit)
            if cut < 0:
                cut = limit
            out.append(p[:cut+1].strip())
            p = p[cut+1:].strip()
        if p:
            out.append(p)
    return out


def synthesize(text, voice='F2', speed=1.0, pitch_shift=0.0, pitch_range=1.0):
    """text -> float32 numpy waveform at 24 kHz (one utterance, <=512 tokens)."""
    if voice not in VOICES:
        raise ValueError(f'voice must be F2 or M2, got {voice!r}')
    phones = dizione.phonemize(text)
    if not phones or not getattr(phones, 'ids', None):
        raise ValueError('nothing in the text could be read: tiny-voca only reads English for now')
    one = lambda v: np.array([v], dtype=np.float32)
    audio, _ = session().run(None, {
        'tokens': np.array([phones.ids], dtype=np.int64),
        'stress': np.array([phones.stress], dtype=np.int64),
        'voice': np.array([VOICES[voice]], dtype=np.int64),
        'speed': one(speed), 'pitch_shift': one(pitch_shift),
        'pitch_range': one(pitch_range),
    })
    a = audio[0].astype(np.float32)
    peak = float(np.abs(a).max()) if a.size else 0.0
    if peak > 0.99:
        a = a * (0.99 / peak)
    return a


def speak_text(text, output, voice='F2', speed=1.0, pitch_shift=0.0, pitch_range=1.0):
    """Long text -> single 16-bit WAV; joins sentences with 180 ms silence."""
    sentences = split_sentences(text)
    if not sentences:
        raise ValueError('nothing in the text could be read')
    chunks = [synthesize(s, voice, speed, pitch_shift, pitch_range) for s in sentences]
    gap = np.zeros(int(SR * 0.18), dtype=np.float32)
    joined = np.concatenate([c for i, c in enumerate(chunks) for c in ([gap] if i else []) + [c]])
    out = Path(output)
    out.parent.mkdir(parents=True, exist_ok=True)
    pcm = (np.clip(joined, -1.0, 1.0) * 32767).astype('<i2')
    with wave.open(str(out), 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    return {'success': True, 'output': str(out), 'voice': voice,
            'sentences': len(sentences), 'duration_s': round(len(joined)/SR, 3),
            'sample_rate': SR, 'sha256': hashlib.sha256(out.read_bytes()).hexdigest()}


def main():
    import argparse
    p = argparse.ArgumentParser(description='tiny-voca local TTS (ONNX)')
    p.add_argument('--text', default=None)
    p.add_argument('--text-file', default=None,
                   help='Read text from UTF-8 file (Hermes TTS provider convention).')
    p.add_argument('--voice', default='M2', choices=['F2', 'M2'])
    p.add_argument('--output', default='/opt/data/tiny-voca-out.wav')
    p.add_argument('--speed', type=float, default=1.0)
    p.add_argument('--pitch-shift', type=float, default=0.0)
    p.add_argument('--pitch-range', type=float, default=1.0)
    a = p.parse_args()
    if a.text_file:
        text = Path(a.text_file).read_text(encoding='utf-8')
    elif a.text:
        text = a.text
    else:
        print(json.dumps({'success': False, 'error': 'text or --text-file is required'}))
        sys.exit(1)
    try:
        r = speak_text(text, a.output, a.voice, a.speed, a.pitch_shift, a.pitch_range)
        print(json.dumps(r))
    except Exception as e:
        print(json.dumps({'success': False, 'error': str(e)})); sys.exit(1)


if __name__ == '__main__':
    main()
