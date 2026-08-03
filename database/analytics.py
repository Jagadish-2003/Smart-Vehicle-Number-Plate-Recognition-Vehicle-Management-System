"""Aggregate queries over the detections table, returned as pandas DataFrames
for use by the analytics page/charts."""
import pandas as pd
from database.database import get_connection


def load_dataframe() -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM detections", conn)
    conn.close()
    if not df.empty:
        df["detection_time"] = pd.to_datetime(df["detection_time"])
    return df


def daily_trend(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["date", "count"])
    grouped = df.groupby(df["detection_time"].dt.date).size().reset_index(name="count")
    grouped.columns = ["date", "count"]
    return grouped


def hourly_trend(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["hour", "count"])
    grouped = df.groupby(df["detection_time"].dt.hour).size().reset_index(name="count")
    grouped.columns = ["hour", "count"]
    return grouped


def top_plates(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["plate_number", "count"])
    grouped = df.groupby("plate_number").size().reset_index(name="count")
    return grouped.sort_values("count", ascending=False).head(n)


def valid_vs_invalid(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["status", "count"])
    grouped = df.groupby("status").size().reset_index(name="count")
    return grouped


def confidence_stats(df: pd.DataFrame) -> dict:
    if df.empty:
        return {"avg_ocr_confidence": 0.0, "avg_detection_confidence": 0.0}
    return {
        "avg_ocr_confidence": round(float(df["ocr_confidence"].mean()), 3),
        "avg_detection_confidence": round(float(df["detection_confidence"].mean()), 3),
    }
