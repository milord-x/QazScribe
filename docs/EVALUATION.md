# Evaluation Plan

## Objective

The evaluation goal is to determine whether QazScribe produces usable meeting
artifacts for institutional workflows: transcripts, speaker-oriented text,
structured notes, summaries, and downloadable documents.

## Test Languages

Minimum evaluation set:

```text
Russian
Kazakh
Kyrgyz
Uzbek
Tatar
Tajik
Azerbaijani
Turkmen
Belarusian
Ukrainian
```

## Test Conditions

Use several controlled scenarios:

- quiet room, one speaker;
- quiet room, two speakers;
- lecture recording from a laptop microphone;
- phone microphone recording;
- mixed Russian/Kazakh or Russian/Kyrgyz speech;
- noisy background recording.

## Metrics

### Quantitative

- word error rate where reference text exists;
- task completion time;
- audio duration vs. processing duration;
- document generation success rate;
- upload success rate.

### Qualitative

- correctness of names, numbers, and terms;
- usefulness of the summary;
- clarity of the full notes;
- readability of exported documents;
- stability of microphone recording on desktop and mobile.

## Known MVP Limits

Speaker separation is currently heuristic. It should not be presented as a
complete diarization system. For production-grade diarization, an additional
speaker embedding or diarization model should be integrated and evaluated
separately.

Browser live captions are draft captions. They are useful for user confidence
during recording, but the server transcript is the authoritative output.
