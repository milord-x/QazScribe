# Speech and Language Models

## Model Strategy

qTranscript uses a multi-model ASR architecture for Kazakh and Kyrgyz
institutional speech. The default production path is a strong multilingual
Whisper model because it can auto-detect closely related languages. Specialized
Kazakh and Kyrgyz Hugging Face models are available as selectable evaluation
backends.

The active backend is configured through environment variables:

```text
ASR_BACKEND=faster_whisper | transformers_whisper | wav2vec2_ctc
ASR_MODEL_SIZE=large-v3
ASR_MODEL_ID=
ASR_TRANSFORMERS_LANGUAGE=
ASR_TRUST_REMOTE_CODE=false
```

## Default Production Model

### `openai/whisper-large-v3` through `faster-whisper`

```text
ASR_BACKEND=faster_whisper
ASR_MODEL_SIZE=large-v3
ASR_MODEL_ID=
ASR_DEVICE=cuda
ASR_COMPUTE_TYPE=float16
```

Whisper large-v3 is the default model for mixed Kazakh/Kyrgyz speech, lectures,
meetings, and formal recordings. The Hugging Face model card
describes Whisper large-v3 as a multilingual ASR model with support for 99
languages. It is used through `faster-whisper` for efficient local GPU
inference.

Source: https://huggingface.co/openai/whisper-large-v3

## Regional Model Catalog

| Language | Recommended model | Backend | Notes |
| --- | --- | --- | --- |
| General multilingual | `openai/whisper-large-v3` | `faster_whisper` | Default production model for Kazakh/Kyrgyz auto-detection. |
| Kazakh | `InflexionLab/sybyrla` | `transformers_whisper` | Whisper Large V3 fine-tuned for Kazakh with Russian auxiliary data. |
| Kyrgyz | `nineninesix/kyrgyz-whisper-medium` | `transformers_whisper` | Kyrgyz/Russian/English model for code-switching scenarios. |
| Kyrgyz comparison | `kyrgyz-ai/Wav2vec-Kyrgyz` | `wav2vec2_ctc` | Kyrgyz-only Wav2Vec2 comparison model. |
| Russian and other CIS reserve | `openai/whisper-large-v3` | `faster_whisper` | Kept in the backend catalog but not exposed in the public frontend. |
| Uzbek | `Uzbekswe/uzbek_stt_v1` | `transformers_whisper` | Whisper Medium Uzbek model; model card reports 16.7% overall WER. |
| Tatar | `501Good/whisper-tiny-tt` | `transformers_whisper` | Experimental Tatar model; use large-v3 as fallback for serious demos. |
| Tajik | `muhtasham/whisper-tg` | `transformers_whisper` | Whisper Small Tajik model; model card reports 18.9518% WER. |
| Azerbaijani | `LocalDoc/azerbaijani-whisper-turbo` | `transformers_whisper` | Azerbaijani Whisper Turbo; model card reports 13.17% WER. |
| Turkmen | `Atamyrat2005/whisper-base-tk-finetuned` | `transformers_whisper` | Whisper model fine-tuned for Turkmen on Common Voice 17.0. |
| Belarusian | `Aleton/whisper-small-be-custom` | `transformers_whisper` | Whisper Small model optimized for Belarusian. |
| Ukrainian | `vumenira/whisper-small-uk` | `transformers_whisper` | Whisper Small Ukrainian model; model card reports 17.2136% WER. |

The full research catalog is exposed by the backend health endpoint:

```text
GET /health/ai
```

## Environment Presets

### Kazakh

```text
ASR_BACKEND=transformers_whisper
ASR_MODEL_ID=InflexionLab/sybyrla
ASR_TRANSFORMERS_LANGUAGE=kazakh
ASR_TRUST_REMOTE_CODE=false
```

### Kyrgyz

```text
ASR_BACKEND=transformers_whisper
ASR_MODEL_ID=nineninesix/kyrgyz-whisper-medium
ASR_TRANSFORMERS_LANGUAGE=kyrgyz
ASR_TRUST_REMOTE_CODE=true
```

### Reserve Models

The following models remain documented for research continuity but are not
exposed in the public frontend. The current client-facing product scope is
Kazakh/Kyrgyz recognition.

#### Uzbek

```text
ASR_BACKEND=transformers_whisper
ASR_MODEL_ID=Uzbekswe/uzbek_stt_v1
ASR_TRANSFORMERS_LANGUAGE=uzbek
ASR_TRUST_REMOTE_CODE=false
```

#### Tajik

```text
ASR_BACKEND=transformers_whisper
ASR_MODEL_ID=muhtasham/whisper-tg
ASR_TRANSFORMERS_LANGUAGE=tajik
ASR_TRUST_REMOTE_CODE=false
```

#### Azerbaijani

```text
ASR_BACKEND=transformers_whisper
ASR_MODEL_ID=LocalDoc/azerbaijani-whisper-turbo
ASR_TRANSFORMERS_LANGUAGE=azerbaijani
ASR_TRUST_REMOTE_CODE=false
```

#### Turkmen

```text
ASR_BACKEND=transformers_whisper
ASR_MODEL_ID=Atamyrat2005/whisper-base-tk-finetuned
ASR_TRANSFORMERS_LANGUAGE=turkmen
ASR_TRUST_REMOTE_CODE=false
```

#### Belarusian

```text
ASR_BACKEND=transformers_whisper
ASR_MODEL_ID=Aleton/whisper-small-be-custom
ASR_TRANSFORMERS_LANGUAGE=belarusian
ASR_TRUST_REMOTE_CODE=false
```

#### Ukrainian

```text
ASR_BACKEND=transformers_whisper
ASR_MODEL_ID=vumenira/whisper-small-uk
ASR_TRANSFORMERS_LANGUAGE=ukrainian
ASR_TRUST_REMOTE_CODE=false
```

## Browser Draft Captions

The frontend supports draft captions for:

```text
Auto, Kazakh, Kyrgyz
```

These captions depend on browser support and are not used as the final
transcript. The server model produces the authoritative text.

## Limitations

ASR accuracy depends on microphone quality, background noise, speaker overlap,
language mixing, domain terminology, and selected model. The current MVP speaker
attribution is heuristic and based on timing gaps; it is not a full neural
speaker diarization system.

## Sources

- https://huggingface.co/openai/whisper-large-v3
- https://huggingface.co/InflexionLab/sybyrla
- https://huggingface.co/nineninesix/kyrgyz-whisper-medium
- https://huggingface.co/kyrgyz-ai/Wav2vec-Kyrgyz
- https://huggingface.co/Uzbekswe/uzbek_stt_v1
- https://huggingface.co/501Good/whisper-tiny-tt
- https://huggingface.co/muhtasham/whisper-tg
- https://huggingface.co/LocalDoc/azerbaijani-whisper-turbo
- https://huggingface.co/Atamyrat2005/whisper-base-tk-finetuned
- https://huggingface.co/Aleton/whisper-small-be-custom
- https://huggingface.co/vumenira/whisper-small-uk
