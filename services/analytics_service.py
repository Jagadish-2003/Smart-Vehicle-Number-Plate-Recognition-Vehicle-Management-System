"""Thin wrapper around database.analytics for use by the Analytics page."""
from database.analytics import (
    load_dataframe, daily_trend, hourly_trend, top_plates,
    valid_vs_invalid, confidence_stats,
)


class AnalyticsService:
    def get_full_report(self) -> dict:
        df = load_dataframe()
        return {
            "dataframe": df,
            "daily_trend": daily_trend(df),
            "hourly_trend": hourly_trend(df),
            "top_plates": top_plates(df),
            "valid_vs_invalid": valid_vs_invalid(df),
            "confidence_stats": confidence_stats(df),
            "row_count": len(df),
        }
