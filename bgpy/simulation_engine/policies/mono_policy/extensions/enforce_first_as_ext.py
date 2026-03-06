"""EnforceFirstAS extension for MonoPolicy."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bgpy.shared.enums import Relationships
    from bgpy.simulation_engine.announcement import Announcement as Ann
    from bgpy.simulation_engine.policies.mono_policy.mono_policy import MonoPolicy


class EnforceFirstASExt:
    """Enforce-First-AS check — first AS-Path entry must be a known neighbor."""

    @staticmethod
    def valid_ann(policy: "MonoPolicy", ann: "Ann", from_rel: "Relationships") -> bool:
        """Return False if the first ASN in the path is not a known neighbor."""
        return (
            ann.next_hop_asn == ann.as_path[0]
            and ann.next_hop_asn
            in getattr(policy.as_, f"{from_rel.name.lower()[:-1]}_asns")
        )
