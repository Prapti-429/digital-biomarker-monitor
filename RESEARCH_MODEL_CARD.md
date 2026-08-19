# NUVYRA Research Model Card

## Purpose

NUVYRA is an observational, multimodal longitudinal research prototype. It combines available voice, facial-dynamics, eye, gait/movement, breathing-proxy and head-movement features with user-provided context to study change relative to an individual's own history.

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

## Missing and noisy data

Missing modalities are never converted into a normal value. Invalid, non-finite and extreme numeric payloads are rejected before entering the baseline. Low-quality sessions are explicitly flagged so that a single poor recording does not silently become evidence of change.

## Persistence logic

A single unusual observation is not labelled as persistent change. Persistence requires sufficient longitudinal history and repeated deviation in recent usable observations. With insufficient history, the engine returns `INSUFFICIENT_HISTORY`.

## Breathing, face, eye, gait and head signals

These are research proxies derived from consumer-device recordings. They are not clinically validated physiological measurements and must not be interpreted as diagnoses.

## Voice analysis

Voice features are acoustic/research features such as pitch, RMS energy, speech activity, speech rate and pause ratio. They are not a clinical speech assessment.

## Stability index

The stability index is experimental. It is a research summary of consistency relative to the user's available longitudinal data, not a medical score and not a measure of disease status.

## Explainability

Every analysis stores the algorithm/model version, data quality, available and missing modalities, baseline size, persistence state, leading feature deviations, recommendations and limitations. These fields are intended to make the inference traceable and understandable.

## Validation status

The repository contains automated regression tests for core research-engine invariants. Automated tests do not constitute clinical validation. Claims about accuracy must be based on a predefined labelled dataset, participant-independent held-out evaluation, appropriate metrics and uncertainty estimates.

## Privacy and security

The application is designed to be privacy-sensitive and includes authentication, authorization, security middleware and audit infrastructure. This repository has not been independently security-audited, so it must not be represented as formally certified or audited for regulatory compliance.

## Safety boundary

NUVYRA must not diagnose disease, recommend treatment changes, or present experimental proxy measurements as confirmed physiological or clinical findings.
