# Voice & Whisper Engine

The product uses Faster-Whisper for speech recognition and Edge TTS for supported neural narration workflows.

## Speech recognition

Configuration variables:

    WHISPER_MODEL=tiny
    WHISPER_DEVICE=cpu

Available model choices reported by the settings endpoint include tiny, base, small, medium and large-v3. Larger models generally require more memory and compute. The first run may download model files.

Device options in the settings model:
- cpu
- cuda
- auto

The auto path attempts CUDA and falls back to CPU if GPU initialization fails. CUDA compatibility depends on the installed runtime, GPU driver and CTranslate2 dependencies.

## Transcription behavior

- The application transcribes media with Faster-Whisper.
- Transcript segments include start/end timestamps and text.
- Voice activity detection is attempted first.
- If too little speech is detected, the implementation retries without VAD.
- Transcripts are used by clip discovery, summaries and caption rendering.

## Voice catalog

The content voice catalog currently includes Turkish and English voices such as:
- tr-TR-EmelNeural
- tr-TR-AhmetNeural
- en-US-AriaNeural
- en-US-GuyNeural
- en-GB-SoniaNeural

The catalog can evolve with the voice provider. Verify the live voice endpoint for current values.

## Important network note

Faster-Whisper can process locally after model files are available. Edge TTS is a network-backed service; it is not an offline voice engine. Do not describe all voice generation as offline.

## Quality checklist

- Verify language selection and detected language.
- Review names, numbers and technical terms.
- Listen for pronunciation and pacing.
- Ensure subtitles match spoken audio.
- Keep source media and generated narration under appropriate access controls.
