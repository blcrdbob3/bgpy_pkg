"""ROV extension for MonoPolicy."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bgpy.shared.enums import Relationships
    from bgpy.simulation_engine.announcement import Announcement as Ann
    from bgpy.simulation_engine.policies.mono_policy.mono_policy import MonoPolicy


class ROVExt:
    """ROV validity check — drop announcements invalid by ROA."""

    @staticmethod
    def valid_ann(policy: "MonoPolicy", ann: "Ann", recv_rel: "Relationships") -> bool:
        """Return False if the announcement is invalid by ROA."""
        return not policy.ann_is_invalid_by_roa(ann)
