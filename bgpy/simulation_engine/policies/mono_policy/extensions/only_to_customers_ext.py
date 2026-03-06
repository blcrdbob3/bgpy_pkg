"""OnlyToCustomers extension for MonoPolicy."""

from __future__ import annotations

from typing import TYPE_CHECKING

from bgpy.shared.enums import Relationships

if TYPE_CHECKING:
    from bgpy.simulation_engine.announcement import Announcement as Ann
    from bgpy.simulation_engine.policies.mono_policy.mono_policy import MonoPolicy


class OnlyToCustomersExt:
    """OTC validity and propagation logic."""

    @staticmethod
    def valid_ann(policy: MonoPolicy, ann: Ann, from_rel: Relationships) -> bool:
        """Return False if OTC attribute is violated."""
        if (
            ann.only_to_customers
            and from_rel.value == Relationships.PEERS.value
            and ann.next_hop_asn != ann.only_to_customers
        ) or (
            ann.only_to_customers
            and from_rel.value == Relationships.CUSTOMERS.value
        ):
            return False
        return True
