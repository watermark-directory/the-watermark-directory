"""GitHub App authentication and write operations for the Watermark Directory backend.

Exposes:
- ``GitHubAppClient`` — JWT → installation token (issue #919)
- ``AdminChecker`` — admin/site-admin permission checks
- ``GHResult`` — typed operation outcome
- Op functions: ``comment_on_pr``, ``add_label``, ``remove_label``,
  ``set_issue_state``, ``set_labels``
"""

from __future__ import annotations

from watermark.github._client import GitHubAppClient
from watermark.github._ops import (
    GHResult,
    add_label,
    comment_on_pr,
    remove_label,
    set_issue_state,
    set_labels,
)
from watermark.github._permissions import AdminChecker

__all__ = [
    "AdminChecker",
    "GHResult",
    "GitHubAppClient",
    "add_label",
    "comment_on_pr",
    "remove_label",
    "set_issue_state",
    "set_labels",
]
