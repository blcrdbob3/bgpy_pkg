"""ASPAwN extension for MonoPolicy."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .aspa_ext import ASPAExt

if TYPE_CHECKING:
    from bgpy.shared.enums import Relationships
    from bgpy.simulation_engine.announcement import Announcement as Ann
    from bgpy.simulation_engine.policies.mono_policy.mono_policy import MonoPolicy


def _is_aspawn_deployer(policy_obj) -> bool:  # type: ignore[no-untyped-def]
    """Return True if policy_obj deploys ASPAwN (original class or MonoPolicy)."""
    from bgpy.simulation_engine.policies.aspa.aspawn import ASPAwN  # noqa: PLC0415

    if isinstance(policy_obj, ASPAwN):
        return True
    settings = getattr(policy_obj, "settings", None)
    if settings is not None and getattr(type(policy_obj), "_IS_MONO_POLICY", False):
        from bgpy.simulation_engine.policies.mono_policy.policy_settings import (  # noqa: PLC0415
            PolicySettings,
        )

        return bool(settings[PolicySettings.ASPAWN])
    return False


class ASPAwNExt:
    """ASPAwN validity checks (ASPA + neighbor-checking at every AS).

    ROV and BGP checks are NOT repeated here.
    """

    @staticmethod
    def valid_ann(policy: MonoPolicy, ann: Ann, from_rel: Relationships) -> bool:
        """Check that each ASPAwN-adopting AS in the path lists both neighbors."""
        as_path = ann.as_path
        as_dict = policy.as_.as_graph.as_dict
        for i, asn in enumerate(as_path):
            asn_obj = as_dict.get(asn)
            if asn_obj and _is_aspawn_deployer(asn_obj.policy):
                for neighbor_index in (i - 1, i + 1):
                    if 0 <= neighbor_index < len(as_path):
                        neighbor_asn = as_path[neighbor_index]
                        if neighbor_asn not in asn_obj.neighbor_asns:
                            return False

        # Then run ASPA logic (without ROV/BGP — those are done separately)
        return ASPAExt.valid_ann(policy, ann, from_rel)
