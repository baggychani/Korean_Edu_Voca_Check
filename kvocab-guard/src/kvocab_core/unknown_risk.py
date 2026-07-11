from __future__ import annotations

from kvocab_core.schemas import IssueStatus, Severity, Strictness


def classify_unknown(
    token: str,
    *,
    strictness: Strictness = Strictness.balanced,
) -> tuple[IssueStatus, Severity, str, list[str]]:
    """Return one neutral status for every item absent from the textbook data.

    ``strictness`` remains in the signature for callers using the older API, but
    no longer changes the result.
    """
    _ = token, strictness
    return IssueStatus.unknown, Severity.medium, "교재에 없는 어휘", []
