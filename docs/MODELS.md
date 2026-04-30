# Speech and Language Models

## Model Strategy

QazScribe uses a multi-model architecture. The default production mode is a
general multilingual ASR model. Additional Hugging Face models can be selected
for regional-language experiments and presentation of model diversity.

## Default ASR

### `openai/whisper-large-v3` through `faster-whisper`

The production default is:

```text
ASR_BACKEND=faster_whisper
ASR_MODEL_SIZE=large-v3
ASR_DEVICE=cuda
ASR_COMPUTE_TYPE=float16
```

Whisper large-v3 is a multilingual automatic speech recognition model. Its
model card describes support for 99 languages and reports improved performance
over large-v2 across many languages. In QazScribe it is used through
`faster-whisper`, which runs Whisper with CTranslate2 for efficient local GPU
inference.

Use this mode for general Russian, Kazakh, mixed speech, lectures, and formal
meeting recordings.

Source: https://huggingface.co/openai/whisper-large-v3

## Optional Regional ASR Models

### `nineninesix/kyrgyz-whisper-medium`

This is a Whisper Medium based model fine-tuned for Kyrgyz while retaining
Russian and English capability. Its model card describes:

- Kyrgyz language support through a custom Kyrgyz token;
- multilingual scope for Kyrgyz, Russian, and English;
- training on Kyrgyz audio with additional English/Russian material;
- suitability for code-switching scenarios.

Recommended use in QazScribe:

```text
ASR_BACKEND=transformers_whisper
ASR_MODEL_ID=nineninesix/kyrgyz-whisper-medium
ASR_TRANSFORMERS_LANGUAGE=kyrgyz
ASR_TRUST_REMOTE_CODE=true
```

Use this mode when the demonstration or evaluation specifically targets Kyrgyz
speech.

Source: https://huggingface.co/nineninesix/kyrgyz-whisper-medium

### `kyrgyz-ai/Wav2vec-Kyrgyz`

This is a Wav2Vec2-Large-XLSR-53 model fine-tuned for Kyrgyz on Common Voice.
The model card reports a self-reported Common Voice Kyrgyz test WER of 34.08%.

Recommended use in QazScribe:

```text
ASR_BACKEND=wav2vec2_ctc
ASR_MODEL_ID=kyrgyz-ai/Wav2vec-Kyrgyz
ASR_TRUST_REMOTE_CODE=false
```

This mode should be treated as an experimental comparison model. It is
Kyrgyz-focused and does not provide the same multilingual robustness as Whisper.

Source: https://huggingface.co/kyrgyz-ai/Wav2vec-Kyrgyz

## Browser Draft Captions

The frontend supports draft captions for:

```text
Russian, Kazakh, Kyrgyz, Uzbek, Tatar, Tajik, Azerbaijani, Turkmen,
Belarusian, Ukrainian
```

These captions depend on the browser implementation and are not used as the
final transcript. Final text is produced by the backend ASR model.

## Model Limitations

ASR accuracy depends on:

- microphone quality;
- distance from speaker to microphone;
- background noise;
- overlap between speakers;
- language mixing;
- domain-specific names and terminology;
- selected ASR backend.

Speaker attribution in the MVP is heuristic and based on timing gaps. It is not
full neural speaker diarization.
