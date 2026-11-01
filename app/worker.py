"""One isolated local inference process. No remote model identifiers accepted."""
import json
import os
from pathlib import Path
import sys


def main():
    model = Path(os.environ.get('AUDIO_MODEL_PATH', ''))
    if not os.environ.get('AUDIO_MODEL_PATH') or not model.is_dir():
        raise RuntimeError('MODEL_NOT_CONFIGURED')
    if not all((model / name).is_file() for name in ('model.bin', 'config.json', 'tokenizer.json')):
        raise RuntimeError('MODEL_FILES_MISSING')
    os.environ['HF_HUB_OFFLINE'] = '1'
    os.environ['TRANSFORMERS_OFFLINE'] = '1'
    from faster_whisper import WhisperModel
    engine = WhisperModel(str(model), device=os.getenv('AUDIO_DEVICE', 'cpu'),
                          compute_type=os.getenv('AUDIO_COMPUTE_TYPE', 'int8'),
                          local_files_only=True)
    segments, _ = engine.transcribe(sys.argv[1], beam_size=5, vad_filter=True)
    result = [{'id': i + 1, 'start': s.start, 'end': s.end, 'text': s.text.strip()}
              for i, s in enumerate(segments)]
    Path(sys.argv[2]).write_text(json.dumps(result, ensure_ascii=False), encoding='utf-8')

if __name__ == '__main__':
    main()
