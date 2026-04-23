"""
Download format strategies for the Strategy pattern used in `download_file`.

Each strategy encapsulates the logic for converting a pandas DataFrame into bytes
for a specific file format, along with the appropriate filename suffix.
"""

import io
from abc import ABC, abstractmethod
from io import StringIO

import pandas as pd
from pandas.core.frame import DataFrame


class DownloadStrategy(ABC):
    """Abstract base class for file download format strategies."""

    @abstractmethod
    def convert(self, df: DataFrame, safe_name: str) -> tuple[bytes, str]:
        """
        Convert a DataFrame to bytes in the target format.

        Args:
            df: The pandas DataFrame to convert.
            safe_name: The base filename (without extension) to use.

        Returns:
            A tuple of (file_bytes, filename).
        """
        ...

    def encode_filename(self, filename: str) -> str:
        """Helper method to percent-encode a UTF-8 filename for Content-Disposition."""
        from urllib.parse import quote
        return quote(filename, safe="")

    def get_content_disposition(self, filename: str) -> str:
        """Generate a Content-Disposition header value with both filename and filename*.

        The legacy ``filename`` parameter is restricted to ASCII/latin-1 so that
        HTTP headers remain valid regardless of the server encoding.  The full
        Unicode filename is carried by the RFC 5987 ``filename*`` parameter.
        """
        encoded_filename = self.encode_filename(filename)
        # Strip / replace non-ASCII chars for the legacy filename= field so the
        # header value never triggers a UnicodeEncodeError in latin-1.
        ascii_filename = filename.encode("ascii", errors="replace").decode("ascii")
        return (
            f"attachment; filename=\"{ascii_filename}\"; "
            f"filename*=UTF-8''{encoded_filename}"
        )


class XlsxDownloadStrategy(DownloadStrategy):
    """Strategy for exporting a DataFrame as an Excel (.xlsx) file."""

    def convert(self, df: DataFrame, safe_name: str) -> tuple[bytes, str]:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:  # type: ignore[abstract]  # ty:ignore[invalid-argument-type]
            df.to_excel(writer, index=False, sheet_name="OCR Tables")
        return output.getvalue(), self.get_content_disposition(f"{safe_name}_tables.xlsx")


class CsvDownloadStrategy(DownloadStrategy):
    """Strategy for exporting a DataFrame as a CSV file."""

    def convert(self, df: DataFrame, safe_name: str) -> tuple[bytes, str]:
        output = StringIO()
        df.to_csv(output, index=False)
        return output.getvalue().encode("utf-8"), self.get_content_disposition(f"{safe_name}_tables.csv")


class JsonDownloadStrategy(DownloadStrategy):
    """Strategy for exporting a DataFrame as a JSON file."""

    def convert(self, df: DataFrame, safe_name: str) -> tuple[bytes, str]:
        text = df.to_json(orient="records", force_ascii=False) or ""
        return text.encode("utf-8"), self.get_content_disposition(f"{safe_name}_tables.json")


class HtmlDownloadStrategy(DownloadStrategy):
    """Strategy for exporting a DataFrame as an HTML table file."""

    def convert(self, df: DataFrame, safe_name: str) -> tuple[bytes, str]:
        text = df.to_html(index=False) or ""
        return text.encode("utf-8"), self.get_content_disposition(f"{safe_name}_tables.html")


# Registry mapping type strings to strategy instances
DOWNLOAD_STRATEGIES: dict[str, DownloadStrategy] = {
    "xlsx": XlsxDownloadStrategy(),
    "csv": CsvDownloadStrategy(),
    "json": JsonDownloadStrategy(),
    "html": HtmlDownloadStrategy(),
}
