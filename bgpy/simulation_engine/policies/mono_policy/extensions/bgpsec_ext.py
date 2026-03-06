"""BGPSec extension for MonoPolicy."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bgpy.as_graphs import AS
    from bgpy.shared.enums import Relationships
    from bgpy.simulation_engine.announcement import Announcement as Ann
    from bgpy.simulation_engine.policies.mono_policy.mono_policy import MonoPolicy


def _is_bgpsec_deployer(policy_obj) -> bool:  # type: ignore[no-untyped-def]
    """Return True if policy_obj deploys BGPSec (original class or MonoPolicy)."""
    from bgpy.simulation_engine.policies.bgpsec.bgpsec import BGPSec  # noqa: PLC0415

    if isinstance(policy_obj, BGPSec):
        return True
    settings = getattr(policy_obj, "settings", None)
    if settings is not None and getattr(type(policy_obj), "_IS_MONO_POLICY", False):
        from bgpy.simulation_engine.policies.mono_policy.policy_settings import (  # noqa: PLC0415
            PolicySettings,
        )

        return bool(settings[PolicySettings.BGPSEC])
    return False


class BGPSecExt:
    """BGPSec helpers: seed, propagate, copy-and-process updates, and tiebreaker."""

    @staticmethod
    def bgpsec_valid(ann: Ann, asn: int) -> bool:
        """Return True if ann carries a valid BGPSec signature for asn."""
        return ann.bgpsec_next_asn == asn and ann.bgpsec_as_path == ann.as_path

    @staticmethod
    def prepare_seed_ann(policy: MonoPolicy, ann: Ann) -> Ann:
        """Initialize bgpsec_as_path when seeding at origin."""
        if ann.as_path == (policy.as_.asn,):
            ann = ann.copy({"bgpsec_as_path": ann.as_path})
        return ann

    @staticmethod
    def bgpsec_propagate(
        policy: MonoPolicy,
        neighbor: AS,
        ann: Ann,
        propagate_to: Relationships,
        send_rels: set[Relationships],
    ) -> bool:
        """Propagate with BGPSec fields; clears them when sending to non-BGPSec."""
        if _is_bgpsec_deployer(neighbor.policy):
            next_asn = neighbor.asn
            path = ann.bgpsec_as_path
        else:
            next_asn = None
            path = ()
        send_ann = ann.copy({"bgpsec_next_asn": next_asn, "bgpsec_as_path": path})
        policy._process_outgoing_ann(neighbor, send_ann, propagate_to, send_rels)  # noqa: SLF001
        return True

    @staticmethod
    def update_copy_kwargs(
        policy: MonoPolicy,
        ann: Ann,
        kwargs: dict,
    ) -> None:
        """Add bgpsec_as_path to kwargs (only if not already set)."""
        if "bgpsec_as_path" not in kwargs:
            if BGPSecExt.bgpsec_valid(ann, policy.as_.asn):
                kwargs["bgpsec_as_path"] = (policy.as_.asn, *ann.bgpsec_as_path)
            else:
                kwargs["bgpsec_as_path"] = ()

    @staticmethod
    def get_best_ann_by_bgpsec(
        policy: MonoPolicy,
        current_ann: Ann,
        new_ann: Ann,
    ) -> Ann | None:
        """Prefer BGPSec-valid announcements; return None on tie."""
        current_valid = BGPSecExt.bgpsec_valid(current_ann, policy.as_.asn)
        new_valid = BGPSecExt.bgpsec_valid(new_ann, policy.as_.asn)
        if current_valid and not new_valid:
            return current_ann
        elif not current_valid and new_valid:
            return new_ann
        return None
