from typing import TYPE_CHECKING, Any, Optional
from warnings import warn

from bgpy.shared.enums import PolicySettingsIndex, Relationships
from bgpy.shared.settings import PolicySettings
from bgpy.simulation_engine.ann_containers import LocalRIB, RecvQueue
from bgpy.simulation_engine.policies.policy import Policy

# Gao rexford functions
from .gao_rexford import (
    _get_best_ann_by_as_path,
    _get_best_ann_by_gao_rexford,
    _get_best_ann_by_local_pref,
    _get_best_ann_by_lowest_neighbor_asn_tiebreaker,
)

# Process incoming announcements
from .process_incoming_funcs import (
    _copy_and_process,
    _get_new_best_ann,
    _reset_q,
    process_incoming_anns,
    receive_ann,
    seed_ann,
)

# Propagation functionality
from .propagate_funcs import (
    _policy_propagate,
    _prev_sent,
    _process_outgoing_ann,
    _propagate,
    propagate_to_customers,
    propagate_to_peers,
    propagate_to_providers,
)

if TYPE_CHECKING:
    from weakref import CallableProxyType

    from bgpy.as_graphs import AS
    from bgpy.simulation_engine.announcement import Announcement


class BGP(Policy):
    name: str = "BGP"

    def __init__(
        self,
        local_rib: LocalRIB | None = None,
        recv_q: RecvQueue | None = None,
        as_: Optional["AS"] = None,
        policy_settings: PolicySettings | None = None,
    ) -> None:
        """Add local rib and data structures here

        This way they can be easily cleared later without having to redo
        the graph

        This is also useful for regenerating an AS from YAML
        """

        self.local_rib = local_rib or LocalRIB()
        self.recv_q = recv_q or RecvQueue()
        # This gets set within the AS class so it's fine
        self.as_: CallableProxyType[AS] = as_  # type: ignore
        self.policy_settings = policy_settings or (
            (False, False),  # ROV
            (False,),  # ENFORCE_FIRST_AS
            (False, False),  # EDGE_FILTER
            (False,),  # PEERLOCK_LITE
            (False,),  # ONLY_TO_CUSTOMERS
            (False,),  # PATH_END
            (False,),  # ASPA
            (False,),  # ROST
        )

    # Propagation functionality
    propagate_to_providers = propagate_to_providers
    propagate_to_customers = propagate_to_customers
    propagate_to_peers = propagate_to_peers
    _propagate = _propagate
    _policy_propagate = _policy_propagate
    _process_outgoing_ann = _process_outgoing_ann
    _prev_sent = _prev_sent

    # Process incoming announcements
    seed_ann = seed_ann
    receive_ann = receive_ann
    process_incoming_anns = process_incoming_anns
    _get_new_best_ann = _get_new_best_ann

    def _valid_ann(
        self,
        ann: "Announcement",
        recv_relationship: "Relationships",
    ) -> bool:
        """Determine if an announcement is valid or should be dropped"""

        # BGP Loop Prevention Check
        # Newly added October 31 2024 - no AS 0 either
        if self.as_.asn in ann.as_path or 0 in ann.as_path:
            return False
        # Enforce-First-AS check if enabled
        enforce_first_as_settings = self.policy_settings[
            PolicySettingsIndex.ENFORCE_FIRST_AS
        ]
        if (
            enforce_first_as_settings[0]
            and not self._enforce_first_as_valid(ann, recv_relationship)
        ):
            return False
        # Edge-Filter check if enabled
        edge_filter_settings = self.policy_settings[PolicySettingsIndex.EDGE_FILTER]
        if (
            edge_filter_settings[0]
            and not self._valid_edge_ann(ann, recv_relationship)
        ):
            return False
        # PeerlockLite check if enabled
        peerlock_lite_settings = self.policy_settings[PolicySettingsIndex.PEERLOCK_LITE]
        if (
            peerlock_lite_settings[0]
            and not self._valid_by_peerlock_lite(ann, recv_relationship)
        ):
            return False
        # ROV check if enabled
        rov_settings = self.policy_settings[PolicySettingsIndex.ROV]
        if rov_settings[0] and self.ann_is_invalid_by_roa(ann):
            return False
        return True

    def _valid_by_peerlock_lite(
        self,
        ann: "Announcement",
        recv_rel: "Relationships",
    ) -> bool:
        """Returns if tier-1 ASes are split by other ASNs that are not t1"""

        if recv_rel == Relationships.CUSTOMERS:
            # Input clique has no providers, so if they are your customer,
            # there is a route leakage
            as_dict = self.as_.as_graph.as_dict
            for asn in ann.as_path:
                if as_dict[asn].input_clique:
                    return False
        return True

    def _valid_edge_ann(
        self,
        ann: "Announcement",
        from_rel: "Relationships",
    ) -> bool:
        """Returns invalid if an edge AS is announcing a path containing other ASNs"""

        neighbor_as_obj = self.as_.as_graph.as_dict[ann.as_path[0]]
        if (neighbor_as_obj.stub or neighbor_as_obj.multihomed) and set(
            ann.as_path
        ) != {neighbor_as_obj.asn}:
            return False
        return True

    def _enforce_first_as_valid(
        self,
        ann: "Announcement",
        from_rel: "Relationships",
    ) -> bool:
        """Ensures the first ASN in the AS-Path is a neighbor

        NOTE: normally this would check for an exact match, but since we don't
        store which ASN the announcement came from anywhere, we just check if it
        is a neighbor to simulate
        """

        return (
            ann.next_hop_asn == ann.as_path[0]
            # Super janky, TODO
            and ann.next_hop_asn
            in getattr(self.as_, f"{from_rel.name.lower()[:-1]}_asns")
        )

    _copy_and_process = _copy_and_process
    _reset_q = _reset_q

    # Gao rexford functions
    _get_best_ann_by_gao_rexford = _get_best_ann_by_gao_rexford
    _get_best_ann_by_local_pref = _get_best_ann_by_local_pref
    _get_best_ann_by_as_path = _get_best_ann_by_as_path
    _get_best_ann_by_lowest_neighbor_asn_tiebreaker = (
        _get_best_ann_by_lowest_neighbor_asn_tiebreaker
    )

    @property
    def _local_rib(self) -> LocalRIB:
        warn(
            "Please use .local_rib instead of ._local_rib. "
            "This will be removed in a later version",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.local_rib

    @property
    def _recv_q(self) -> RecvQueue:
        warn(
            "Please use .recv_q instead of ._recv_q. "
            "This will be removed in a later version",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.recv_q

    ##############
    # Yaml funcs #
    ##############

    def __to_yaml_dict__(self) -> dict[Any, Any]:
        """This optional method is called when you call yaml.dump()"""

        return {"local_rib": self.local_rib, "recv_q": self.recv_q}

    @classmethod
    def __from_yaml_dict__(cls, dct, yaml_tag) -> Policy:
        """This optional method is called when you call yaml.load()"""

        return cls(**dct)
