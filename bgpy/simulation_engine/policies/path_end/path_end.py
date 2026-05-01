from typing import TYPE_CHECKING

from bgpy.simulation_engine.policies.rov import ROV

if TYPE_CHECKING:
    from bgpy.shared.enums import PolicySettingsIndex, Relationships
    from bgpy.simulation_engine import Announcement as Ann


class PathEnd(ROV):
    """An Policy that deploys Path-End"""

    name: str = "Path-End"

    def _valid_ann(self, ann: "Ann", recv_rel: "Relationships") -> bool:
        """Returns announcement validity by checking pathend records"""

        path_end_settings = self.policy_settings[PolicySettingsIndex.PATH_END]
        if not path_end_settings[0]:
            return super()._valid_ann(ann, recv_rel)
        origin_asn = ann.origin
        origin_as_obj = self.as_.as_graph.as_dict.get(origin_asn)
        # If the origin is deploying pathend and the path is longer than 1
        if (
            origin_as_obj
            and isinstance(origin_as_obj.policy, PathEnd)
            and len(ann.as_path) > 1
        ):
            # If the provider is real, do the loop check
            # Mypy thinks this is unreachable for some reason, even tho tests pass
            for neighbor in origin_as_obj.neighbors:
                if neighbor.asn == ann.as_path[-2]:
                    return super()._valid_ann(ann, recv_rel)
            # Provider is fake, return False
            return False
        else:
            return super()._valid_ann(ann, recv_rel)
