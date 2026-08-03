"""Plotly chart builders used by the Analytics page."""
import plotly.express as px
import pandas as pd


def daily_trend_chart(df: pd.DataFrame):
    if df.empty:
        return None
    return px.line(df, x="date", y="count", title="Daily Detection Trend", markers=True)


def hourly_trend_chart(df: pd.DataFrame):
    if df.empty:
        return None
    return px.bar(df, x="hour", y="count", title="Hourly Detection Trend")


def top_plates_chart(df: pd.DataFrame):
    if df.empty:
        return None
    return px.bar(df, x="plate_number", y="count", title="Top Detected Plates")


def valid_invalid_pie(df: pd.DataFrame):
    if df.empty:
        return None
    return px.pie(df, names="status", values="count", title="Valid vs Invalid Plates")


def confidence_histogram(df: pd.DataFrame, column: str, title: str):
    if df.empty or column not in df.columns:
        return None
    return px.histogram(df, x=column, nbins=20, title=title)
