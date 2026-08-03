"""Thin wrapper around database.database for use by the History page."""
import pandas as pd
from database.database import (
    search_detections, delete_detection, delete_all_detections,
)


class HistoryService:
    def get_history(self, query: str = "", status: str = "all", limit: int = 500) -> pd.DataFrame:
        rows = search_detections(query=query, status=status, limit=limit)
        return pd.DataFrame(rows)

    def delete(self, detection_id: int) -> bool:
        return delete_detection(detection_id)

    def delete_all(self) -> bool:
        return delete_all_detections()

    def export_csv(self, df: pd.DataFrame) -> bytes:
        return df.to_csv(index=False).encode("utf-8")
