"""Typed document models used by services, workers, and UI."""

from dataclasses import dataclass


@dataclass(frozen=True)
class DocumentInfo:
    """Normalized representation of one open Solid Edge document."""

    name: str
    full_name: str
    document_type: str
    is_active: bool = False

    @property
    def selection_key(self) -> str:
        """Stable selection key used for list re-selection after refresh/sort."""
        return f"{self.full_name.strip().lower()}|{self.name.strip().lower()}"

    @property
    def list_label(self) -> str:
        """Formatted label shown in the navbar list."""
        active_suffix = " (Active)" if self.is_active else ""
        return f"[{self.document_type}] {self.name}{active_suffix}"
