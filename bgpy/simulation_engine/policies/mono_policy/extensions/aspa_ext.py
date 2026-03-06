"""ASPA extension for MonoPolicy."""

from __future__ import annotations

from typing import TYPE_CHECKING

from bgpy.shared.enums import Relationships

if TYPE_CHECKING:
    from bgpy.simulation_engine.announcement import Announcement as Ann
    from bgpy.simulation_engine.policies.mono_policy.mono_policy import MonoPolicy


def _is_aspa_deployer(policy_obj) -> bool:  # type: ignore[no-untyped-def]
    """Return True if policy_obj deploys ASPA (original class or MonoPolicy)."""
    from bgpy.simulation_engine.policies.aspa.aspa import ASPA  # noqa: PLC0415

    if isinstance(policy_obj, ASPA):
        return True
    settings = getattr(policy_obj, "settings", None)
    if settings is not None and getattr(type(policy_obj), "_IS_MONO_POLICY", False):
        from bgpy.simulation_engine.policies.mono_policy.policy_settings import (  # noqa: PLC0415
            PolicySettings,
        )

        return bool(settings[PolicySettings.ASPA])
    return False


class ASPAExt:
    """ASPA validity checks (upstream and downstream).

    ROV and BGP checks are NOT repeated here — they run as separate steps
    in MonoPolicy._valid_ann before this extension is called.
    """

    @staticmethod
    def valid_ann(policy: MonoPolicy, ann: Ann, from_rel: Relationships) -> bool:
        """Return False if ASPA checks fail; True otherwise."""
        # ASPA requires next_hop to be the first AS in the path
        if ann.next_hop_asn != ann.as_path[0]:
            return False

        if from_rel.value == Relationships.PROVIDERS.value:
            return ASPAExt._downstream_check(policy, ann)
        elif from_rel.value in (
            Relationships.CUSTOMERS.value,
            Relationships.PEERS.value,
        ):
            return ASPAExt._upstream_check(policy, ann)
        else:
            raise NotImplementedError("Unexpected relationship in ASPA check")

    @staticmethod
    def _upstream_check(policy: MonoPolicy, ann: Ann) -> bool:
        """ASPA upstream check (received from customer or peer)."""
        if len(ann.as_path) == 1:
            return True
        if ASPAExt._get_max_up_ramp_length(policy, ann) < len(ann.as_path):
            return False
        return True

    @staticmethod
    def _downstream_check(policy: MonoPolicy, ann: Ann) -> bool:
        """ASPA downstream check (received from provider)."""
        max_up = ASPAExt._get_max_up_ramp_length(policy, ann)
        max_down = ASPAExt._get_max_down_ramp_length(policy, ann)
        if max_up + max_down < len(ann.as_path):
            return False
        return True

    @staticmethod
    def _get_max_up_ramp_length(policy: MonoPolicy, ann: Ann) -> int:
        """Compute maximum up-ramp length per ASPA RFC."""
        reversed_path = ann.as_path[::-1]
        for i in range(len(reversed_path) - 1):
            if not ASPAExt._provider_check(  # type: ignore[misc]
                policy, reversed_path[i], reversed_path[i + 1]
            ):
                return i + 1
        return len(ann.as_path)

    @staticmethod
    def _get_max_down_ramp_length(policy: MonoPolicy, ann: Ann) -> int:
        """Compute maximum down-ramp length per ASPA RFC."""
        reversed_path = ann.as_path[::-1]
        for i in range(len(reversed_path) - 1, 0, -1):
            if not ASPAExt._provider_check(  # type: ignore[misc]
                policy, reversed_path[i], reversed_path[i - 1]
            ):
                j = i + 1
                return len(reversed_path) - j + 1
        return len(ann.as_path)

    @staticmethod
    def _provider_check(policy: MonoPolicy, asn1: int, asn2: int) -> bool:
        """Return False if asn2 not in asn1's providers AND asn1 deploys ASPA."""
        cur_as_obj = policy.as_.as_graph.as_dict.get(asn1)
        if cur_as_obj and _is_aspa_deployer(cur_as_obj.policy):
            next_as_obj = policy.as_.as_graph.as_dict.get(asn2)
            next_asn = next_as_obj.asn if next_as_obj else next_as_obj
            if next_asn not in cur_as_obj.provider_asns:
                return False
        return True
