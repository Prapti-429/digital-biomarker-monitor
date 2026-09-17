# NUVYRA Research Model Card

## Purpose

NUVYRA is an observational, multimodal longitudinal research prototype. It combines available voice, facial-dynamics, eye, movement/gait, breathing-proxy and head-movement features with user-provided context to study change relative to an individual's own history.

## What the system does

1. Captures daily multimodal signals.
2. Rejects invalid numeric values and excludes unavailable signals.
3. Calculates a data-quality score from signal coverage, finite feature coverage and recording duration.
4. Builds a personal baseline from prior usable observations using robust median/MAD statistics.
5. Calculates feature-level deviations from that personal baseline.
6. Uses reliability-aware multimodal evidence and, when enough compatible history exists, an Isolation Forest anomaly model.
7. Checks whether notable deviations persist across recent observations.
8. Produces an experimental stability index with confidence, available modalities, missing modalities, drivers, recommendations and limitations.
9. Keeps document/history context separate from biometric evidence and labels it as contextual information.

## Evidence-aware interpretation policy

NUVYRA separates measurement from interpretation. Each signal should be presented according to the strongest claim supported by the available evidence:

- **Established measurement:** a directly measured quantity with a well-defined acquisition method, such as a recorded acoustic amplitude feature. This does not make the measurement disease-specific.
- **Research-supported association:** a feature for which peer-reviewed literature reports associations with a health outcome in a defined population/task. The association is not treated as a diagnosis and may not generalize to NUVYRA's consumer-device setting.
- **Experimental NUVYRA proxy:** a computational estimate derived from ordinary camera/microphone recordings whose reliability or clinical usefulness has not been established for the NUVYRA implementation.
- **Contextual self-report:** participant-reported information such as fatigue, sleep quality, stress, concentration, comfort or appetite. These provide context and are not clinical assessments.

The application must describe what was observed, how it was obtained, relevant confounders, what a change may mean for longitudinal monitoring, and the measurement's limitation. It must not convert an association into a disease claim.

## Measurement boundaries

Voice features such as pitch, RMS energy, zero-crossing rate, speech activity, speech rate and pause proportion are acoustic/research features, not a clinical speech-language assessment. Facial, eye/blink, movement/gait, breathing and head-movement values derived from ordinary consumer-device recordings are research proxies unless a specific validated measurement protocol is used.

A proxy must not be described as a confirmed physiological measurement. In particular, generic frame-difference or luminance calculations must not be presented as a validated gait, blink or respiratory-rate measurement merely because the output has a familiar unit or label.

## Missing and noisy data

Missing modalities are never converted into a normal value. Invalid, non-finite and extreme numeric payloads are rejected before entering the baseline. Low-quality sessions are explicitly flagged so that a single poor recording does not silently become evidence of change.

## Persistence logic

A single unusual observation is not labelled as persistent change. Persistence requires sufficient longitudinal history and repeated deviation in recent usable observations. With insufficient history, the engine returns `INSUFFICIENT_HISTORY`.

## Stability index

The stability index is experimental. It is a research summary of consistency relative to the user's available longitudinal data, not a medical score and not a measure of disease status. Its numeric value must not be presented as a probability of health, disease, recovery or deterioration.

## Explainability

Every analysis stores the algorithm/model version, data quality, available and missing modalities, baseline size, persistence state, leading feature deviations, recommendations and limitations. These fields are intended to make the inference traceable and understandable.

## Validation status

The repository contains automated regression tests for core research-engine invariants. Automated tests do not constitute clinical validation. Claims about accuracy must be based on a predefined labelled dataset, participant-independent held-out evaluation, appropriate metrics and uncertainty estimates. The literature also shows substantial heterogeneity across recording devices, tasks, languages, populations and algorithms, so evidence from another study must not be presented as validation of NUVYRA itself.

## Privacy and security

The application is designed to be privacy-sensitive and includes authentication, authorization, security middleware and audit infrastructure. This repository has not been independently security-audited, so it must not be represented as formally certified or audited for regulatory compliance.

## Safety boundary

NUVYRA must not diagnose disease, recommend treatment changes, triage emergencies, or present experimental proxy measurements as confirmed physiological or clinical findings. A persistent change is a reason for longitudinal review and, where appropriate, discussion with a qualified healthcare professional—not a diagnosis.
