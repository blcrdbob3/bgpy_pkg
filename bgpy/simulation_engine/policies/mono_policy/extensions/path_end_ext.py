"""Path-End extension for MonoPolicy."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bgpy.shared.enums import Relationships
    from bgpy.simulation_engine.announcement import Announcement as Ann
    from bgpy.simulation_engine.policies.mono_policy.mono_policy import MonoPolicy


def _is_path_end_deployer(policy_obj) -> bool:  # type: ignore[no-untyped-def]
    """Return True if policy_obj deploys Path-End (original or MonoPolicy)."""
    from bgpy.simulation_engine.policies.mono_policy.policy_settings import (  # noqa: PLC0415
        PolicySettings,
    )
    from bgpy.simulation_engine.policies.path_end.path_end import (  # noqa: PLC0415
        PathEnd,
    )

    if isinstance(policy_obj, PathEnd):
        return True
    settings = getattr(policy_obj, "settings", None)
    if settings is not None and getattr(type(policy_obj), "_IS_MONO_POLICY", False):
        return bool(settings[PolicySettings.PATH_END])
    return False


class PathEndExt:
    """Path-End check — origin must list its provider in neighbor records."""

    @staticmethod
    def valid_ann(policy: MonoPolicy, ann: Ann, recv_rel: Relationships) -> bool:
        """Return False if origin deploys Path-End but the previous hop is unknown."""
        origin_asn = ann.origin
        origin_as_obj = policy.as_.as_graph.as_dict.get(origin_asn)
        if (
            origin_as_obj
            and _is_path_end_deployer(origin_as_obj.policy)
            and len(ann.as_path) > 1
        ):
            for neighbor in origin_as_obj.neighbors:
                if neighbor.asn == ann.as_path[-2]:
                    return True
            return False
        return True
