"""ProviderConeID extension for MonoPolicy."""

from __future__ import annotations

from typing import TYPE_CHECKING

from bgpy.shared.enums import Relationships

if TYPE_CHECKING:
    from bgpy.simulation_engine.announcement import Announcement as Ann
    from bgpy.simulation_engine.policies.mono_policy.mono_policy import MonoPolicy


def _is_provider_cone_deployer(policy_obj) -> bool:  # type: ignore[no-untyped-def]
    """Return True if policy_obj deploys ProviderConeID (original or MonoPolicy)."""
    from bgpy.simulation_engine.policies.bgpisec.provider_cone_id import (  # noqa: PLC0415
        ProviderConeID,
    )

    if isinstance(policy_obj, ProviderConeID):
        return True
    settings = getattr(policy_obj, "settings", None)
    if settings is not None and getattr(type(policy_obj), "_IS_MONO_POLICY", False):
        from bgpy.simulation_engine.policies.mono_policy.policy_settings import (  # noqa: PLC0415
            PolicySettings,
        )

        return bool(
            settings[PolicySettings.PROVIDER_CONE_ID]
            or settings[PolicySettings.BGP_I_SEC]
        )
    return False


class ProviderConeIDExt:
    """ProviderConeID validity check.

    Ensures all adopting ASes in the path are in the origin's provider cone.
    ROV and BGP checks are NOT repeated here.
    """

    @staticmethod
    def valid_ann(policy: MonoPolicy, ann: Ann, from_rel: Relationships) -> bool:
        """Return False if a provider-cone-adopting AS is outside the origin's cone."""
        if from_rel != Relationships.CUSTOMERS:
            return True

        as_dict = policy.as_.as_graph.as_dict
        provider_cone_asns = as_dict[ann.origin].provider_cone_asns
        if provider_cone_asns is None:
            raise ValueError(
                "Provider cones must be set for ProviderConeID to work, "
                "see params to simulation.py in the simulation_framework of bgpy"
            )
        for asn in (policy.as_.asn, *ann.as_path[:-1]):
            if asn not in provider_cone_asns and _is_provider_cone_deployer(
                as_dict[asn].policy
            ):
                return False
        return True
