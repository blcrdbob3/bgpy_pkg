"""EdgeFilter extension for MonoPolicy."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bgpy.shared.enums import Relationships
    from bgpy.simulation_engine.announcement import Announcement as Ann
    from bgpy.simulation_engine.policies.mono_policy.mono_policy import MonoPolicy


class EdgeFilterExt:
    """EdgeFilter check — prevent edge ASes from announcing other ASNs."""

    @staticmethod
    def valid_ann(policy: "MonoPolicy", ann: "Ann", from_rel: "Relationships") -> bool:
        """Return False if an edge AS announces a path with other ASNs."""
        neighbor_as_obj = policy.as_.as_graph.as_dict[ann.as_path[0]]
        if (neighbor_as_obj.stub or neighbor_as_obj.multihomed) and set(
            ann.as_path
        ) != {neighbor_as_obj.asn}:
            return False
        return True
