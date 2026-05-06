# Evaluation Plan

## Objective

The evaluation goal is to determine whether qTranscript produces usable
Kazakh/Kyrgyz transcripts and export documents for institutional workflows.

## Test Languages

Minimum evaluation set:

```text
Kazakh
Kyrgyz
Kazakh/Kyrgyz mixed or uncertain speech
```

## Test Conditions

Use several controlled scenarios:

- quiet room, one speaker;
- quiet room, two speakers;
- lecture recording from a laptop microphone;
- phone microphone recording;
- mixed Kazakh/Kyrgyz speech;
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
- correctness of Kazakh vs. Kyrgyz language detection;
- clarity of the transcript;
- readability of exported documents;
- stability of microphone recording on desktop and mobile.

## Known MVP Limits

Speaker separation is currently heuristic. It should not be presented as a
complete diarization system. For production-grade diarization, an additional
speaker embedding or diarization model should be integrated and evaluated
separately.

Browser live captions are draft captions. They are useful for user confidence
during recording, but the server transcript is the authoritative output.
