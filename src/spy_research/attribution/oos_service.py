"""Fail-closed Stage 15.2 orchestration over untouched historical years."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from spy_research.attribution.oos_analysis import analyze_oos_period
from spy_research.attribution.oos_models import (
    OOSCandidate,
    OOSClassification,
    OOSOverallResult,
    OOSValidationReport,
    frozen_oos_design,
)
from spy_research.attribution.service import BaseShortAttributionService
from spy_research.bars import ProcessedFiveMinuteStore, ProcessedFiveMinuteValidator
from spy_research.config import ResearchConfig
from spy_research.data import RawBarStore
from spy_research.data.validation import RawDataValidator
from spy_research.levels import (
    OpeningFiveMinuteLevelsService,
    PremarketLevelsService,
    PreviousDayLevelsService,
)
from spy_research.market import XNYSCalendar


DEFAULT_OOS_RAW_DATA_ROOT = Path("data/oos/raw")
DEFAULT_OOS_PROCESSED_DATA_ROOT = Path("data/oos/processed")


class OOSDataQualityError(ValueError):
    """An untouched year cannot safely enter outcome comparison."""


def overall_oos_results(reports, combined):
    overall = []
    for candidate in OOSCandidate:
        year_rows = [
            next(item for item in report.candidates if item.candidate is candidate)
            for report in reports
        ]
        combined_row = next(
            item for item in combined.candidates if item.candidate is candidate
        )
        all_directional = candidate is OOSCandidate.BASE_SHORT_CONTROL or all(
            item.mean_r_delta is not None and item.mean_r_delta > 0
            for item in year_rows
        )
        if candidate is OOSCandidate.BASE_SHORT_CONTROL:
            classification = OOSClassification.DESCRIPTIVELY_REPLICATED
        elif any(
            item.classification is OOSClassification.INSUFFICIENT_OOS_DATA
            for item in year_rows
        ):
            classification = OOSClassification.INSUFFICIENT_OOS_DATA
        elif all(
            item.classification
            is OOSClassification.OOS_REPLICATED_RESEARCH_CANDIDATE
            for item in year_rows
        ):
            classification = OOSClassification.OOS_REPLICATED_RESEARCH_CANDIDATE
        elif not all_directional:
            classification = OOSClassification.FAILED_TO_REPLICATE
        else:
            classification = OOSClassification.DESCRIPTIVELY_REPLICATED
        overall.append(OOSOverallResult(
            candidate=candidate,
            year_mean_r_deltas=tuple(
                (report.period, row.mean_r_delta)
                for report, row in zip(reports, year_rows, strict=True)
            ),
            combined_mean_r_delta=combined_row.mean_r_delta,
            all_unseen_years_directionally_agree=all_directional,
            classification=classification,
        ))
    return tuple(overall)


class OOSExclusionValidationService:
    def __init__(
        self,
        config: ResearchConfig,
        processed_store: ProcessedFiveMinuteStore,
        raw_store: RawBarStore,
        *,
        calendar: XNYSCalendar | None = None,
    ) -> None:
        self._config = config
        self._processed = processed_store
        self._raw = raw_store
        self._calendar = calendar or XNYSCalendar()

    def _gate(self, start: date, end: date) -> None:
        raw = RawDataValidator(self._calendar).validate_raw_store(
            self._raw,
            symbol=self._config.symbol,
            start_date=start,
            end_date=end,
        )
        if (
            not raw.passed
            or raw.sessions_present != raw.expected_sessions
            or raw.missing_rth_bars
            or raw.extra_rth_bars
            or raw.duplicate_keys
        ):
            raise OOSDataQualityError(f"raw OOS gate failed for {start.year}")
        processed = ProcessedFiveMinuteValidator(self._calendar).validate_store(
            self._processed,
            start=start,
            end=end,
            reconcile=True,
            config=self._config,
            raw_store=self._raw,
        )
        if not processed.passed:
            raise OOSDataQualityError(f"processed OOS gate failed for {start.year}")
        previous = PreviousDayLevelsService(
            self._config, self._raw, calendar=self._calendar
        ).calculate(start=start, end=end)
        premarket = PremarketLevelsService(
            self._config, self._raw, calendar=self._calendar
        ).calculate(start=start, end=end)
        opening = OpeningFiveMinuteLevelsService(
            self._config, self._processed, self._raw, calendar=self._calendar
        ).calculate(start=start, end=end)
        expected = raw.expected_sessions
        if (
            previous.missing_sources
            or len(previous.levels) != expected
            or len(premarket.levels) != expected
            or any(item.status != "AVAILABLE" for item in premarket.levels)
            or len(opening.levels) != expected
        ):
            raise OOSDataQualityError(f"level/context OOS gate failed for {start.year}")

    def calculate(self) -> OOSValidationReport:
        design = frozen_oos_design()
        service = BaseShortAttributionService(
            self._config,
            self._processed,
            self._raw,
            calendar=self._calendar,
            allow_oos_execution=True,
        )
        reports = []
        observations_by_year = {}
        for period in design.periods:
            self._gate(period.start_date, period.end_date)
            _unused, observations = service.calculate_with_observations(
                start=period.start_date,
                end=period.end_date,
            )
            observations_by_year[period.year] = observations
            reports.append(analyze_oos_period(
                observations,
                period=str(period.year),
                start_date=period.start_date,
                end_date=period.end_date,
            ))
        combined_observations = tuple(sorted(
            observations_by_year[2024] + observations_by_year[2025],
            key=lambda item: (item.session_date, item.signal_known_at, item.setup_identity),
        ))
        combined = analyze_oos_period(
            combined_observations,
            period="COMBINED_2024_2025",
            start_date=date(2024, 1, 2),
            end_date=date(2025, 12, 31),
        )
        overall = overall_oos_results(reports, combined)
        return OOSValidationReport(
            design=design,
            years=tuple(reports),
            combined=combined,
            overall=overall,
        )
