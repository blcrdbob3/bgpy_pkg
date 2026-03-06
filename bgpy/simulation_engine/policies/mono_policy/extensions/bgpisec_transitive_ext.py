"""BGPiSec Transitive extension for MonoPolicy."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bgpy.shared.enums import Relationships
    from bgpy.simulation_engine.announcement import Announcement as Ann
    from bgpy.simulation_engine.policies.mono_policy.mono_policy import MonoPolicy


def _is_bgpisec_transitive_deployer(policy_obj) -> bool:  # type: ignore[no-untyped-def]
    """Return True if policy_obj deploys BGPiSecTransitive (or MonoPolicy variant)."""
    from bgpy.simulation_engine.policies.bgpisec.bgpisec_transitive import (  # noqa: PLC0415
        BGPiSecTransitive,
    )

    if isinstance(policy_obj, BGPiSecTransitive):
        return True
    settings = getattr(policy_obj, "settings", None)
    if settings is not None and getattr(type(policy_obj), "_IS_MONO_POLICY", False):
        from bgpy.simulation_engine.policies.mono_policy.policy_settings import (  # noqa: PLC0415
            PolicySettings,
        )

        return bool(
            settings[PolicySettings.BGP_I_SEC_TRANSITIVE]
            or settings[PolicySettings.BGP_I_SEC]
        )
    return False


class BGPiSecTransitiveExt:
    """BGPiSec Transitive validity check.

    Verifies that all adopting ASes in the path have signatures.
    ROV and BGP checks are NOT repeated here.
    """

    @staticmethod
    def valid_ann(policy: MonoPolicy, ann: Ann, from_rel: Relationships) -> bool:
        """Return False if any adopting AS in the path is missing a signature."""
        as_graph = policy.as_.as_graph
        bgpsec_signatures = ann.bgpsec_as_path
        for asn in ann.as_path:
            if asn not in bgpsec_signatures and _is_bgpisec_transitive_deployer(
                as_graph.as_dict[asn].policy
            ):
                return False
        return True

    @staticmethod
    def update_copy_kwargs(
        policy: MonoPolicy,
        ann: Ann,
        kwargs: dict,
    ) -> None:
        """Always prepend ASN to bgpsec_as_path (only if not already set)."""
        if "bgpsec_as_path" not in kwargs:
            kwargs["bgpsec_as_path"] = (policy.as_.asn, *ann.bgpsec_as_path)
