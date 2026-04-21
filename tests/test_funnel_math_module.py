"""Sanity checks on funnel_math helpers."""

from __future__ import annotations

from chd_analytics.funnel_math import modeled_diagnoses


def test_modeled_diagnoses_identity():
    assert modeled_diagnoses(1000, 0.5, 0.8, 0.6) == 240.0
