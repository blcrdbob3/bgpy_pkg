"""PeerlockLite extension for MonoPolicy."""

from __future__ import annotations

from typing import TYPE_CHECKING

from bgpy.shared.enums import Relationships

if TYPE_CHECKING:
    from bgpy.simulation_engine.announcement import Announcement as Ann
    from bgpy.simulation_engine.policies.mono_policy.mono_policy import MonoPolicy


class PeerlockLiteExt:
    """Peerlock Lite check — drop customer announcements containing tier-1 ASes."""

    @staticmethod
    def valid_ann(policy: MonoPolicy, ann: Ann, recv_rel: Relationships) -> bool:
        """Return False if a customer-received ann contains input-clique ASes."""
        as_dict = policy.as_.as_graph.as_dict
        if recv_rel == Relationships.CUSTOMERS:
            for asn in ann.as_path:
                if as_dict[asn].input_clique:
                    return False
        return True
