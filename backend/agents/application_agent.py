from __future__ import annotations


class ApplicationAgent:
    """Maintains the hard boundary between assistance and external action."""

    def can_submit(self, explicit_user_approval: bool, requires_manual_intervention: bool = False) -> bool:
        return bool(explicit_user_approval and not requires_manual_intervention)

    def approval_message(self) -> str:
        return 'Applications and outreach are prepared for review only. Nothing is submitted or sent without explicit approval.'
