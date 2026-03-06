"""PeerROV extension for MonoPolicy."""

from __future__ import annotations

from typing import TYPE_CHECKING

from bgpy.shared.enums import Relationships

if TYPE_CHECKING:
    from bgpy.simulation_engine.announcement import Announcement as Ann
    from bgpy.simulation_engine.policies.mono_policy.mono_policy import MonoPolicy


class PeerROVExt:
    """PeerROV validity check — drop ROA-invalid anns that came from peers."""

    @staticmethod
    def valid_ann(policy: MonoPolicy, ann: Ann, recv_rel: Relationships) -> bool:
        """Return False if invalid by ROA and ann.recv_relationship is PEERS."""
        if (
            policy.ann_is_invalid_by_roa(ann)
            and ann.recv_relationship == Relationships.PEERS
        ):
            return False
        return True
