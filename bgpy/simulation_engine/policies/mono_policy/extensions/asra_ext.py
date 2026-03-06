"""ASRA extension for MonoPolicy."""

from __future__ import annotations

from typing import TYPE_CHECKING

from bgpy.shared.enums import Relationships

from .aspa_ext import ASPAExt, _is_aspa_deployer

if TYPE_CHECKING:
    from bgpy.simulation_engine.announcement import Announcement as Ann
    from bgpy.simulation_engine.policies.mono_policy.mono_policy import MonoPolicy


def _is_asra_deployer(policy_obj) -> bool:  # type: ignore[no-untyped-def]
    """Return True if policy_obj deploys ASRA (original class or MonoPolicy)."""
    from bgpy.simulation_engine.policies.aspa.asra import ASRA  # noqa: PLC0415

    if isinstance(policy_obj, ASRA):
        return True
    settings = getattr(policy_obj, "settings", None)
    if settings is not None and getattr(type(policy_obj), "_IS_MONO_POLICY", False):
        from bgpy.simulation_engine.policies.mono_policy.policy_settings import (  # noqa: PLC0415
            PolicySettings,
        )

        return bool(settings[PolicySettings.ASRA])
    return False


class ASRAExt:
    """ASRA validity checks (extends ASPA with fake-link detection).

    ROV and BGP checks are NOT repeated here.
    """

    @staticmethod
    def valid_ann(policy: MonoPolicy, ann: Ann, from_rel: Relationships) -> bool:
        """Run ASPA check first, then ASRA-B fake-link check for PROVIDERS."""
        # First run ASPA logic (without ROV/BGP — those are done separately)
        if not ASPAExt.valid_ann(policy, ann, from_rel):
            return False

        # ASRA-B additional check only for announcements received from providers
        if from_rel != Relationships.PROVIDERS:
            return True

        path = ann.as_path[::-1]
        n = len(path)
        min_up_ramp = ASRAExt._get_min_up_ramp_length(policy, ann)

        if min_up_ramp == n:
            return True

        for i in range(min_up_ramp, n - 1):
            if ASRAExt._is_fake_link(policy, path[i], path[i + 1]):
                return False

        return True

    @staticmethod
    def _get_min_up_ramp_length(policy: MonoPolicy, ann: Ann) -> int:
        """Compute minimum up-ramp length for ASRA-B."""
        path = ann.as_path[::-1]
        for i in range(len(path) - 1):
            asn1 = path[i]
            asn2 = path[i + 1]
            asn1_obj = policy.as_.as_graph.as_dict.get(asn1)
            if not asn1_obj or not _is_aspa_deployer(asn1_obj.policy):
                return i
            if asn2 not in asn1_obj.provider_asns:
                return i
        return len(path)

    @staticmethod
    def _is_fake_link(policy: MonoPolicy, asn1: int, asn2: int) -> bool:
        """ASRA-B fake link check."""
        asn1_obj = policy.as_.as_graph.as_dict.get(asn1)
        has_aspa_but_not_provider = (
            asn1_obj
            and _is_aspa_deployer(asn1_obj.policy)
            and asn2 not in asn1_obj.provider_asns
        )
        has_asra_but_not_neighbor = (
            asn1_obj
            and _is_asra_deployer(asn1_obj.policy)
            and asn2 not in asn1_obj.neighbor_asns
        )
        return bool(has_aspa_but_not_provider and has_asra_but_not_neighbor)
