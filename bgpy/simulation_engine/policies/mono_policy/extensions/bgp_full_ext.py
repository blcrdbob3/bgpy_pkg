"""BGPFull extension for MonoPolicy.

Provides static-method copies of BGPFull's instance methods that use
explicit function dispatch instead of super(), so they can be called
on a MonoPolicy instance that does not inherit from BGPFull.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from bgpy.shared.enums import Relationships

if TYPE_CHECKING:
    from bgpy.simulation_engine.announcement import Announcement as Ann
    from bgpy.simulation_engine.policies.mono_policy.mono_policy import MonoPolicy


class BGPFullExt:
    """Static copies of BGPFull methods for delegation from MonoPolicy."""

    # -------------------------------------------------------------------------
    # process_incoming_anns
    # -------------------------------------------------------------------------

    @staticmethod
    def process_incoming_anns(
        policy: MonoPolicy,
        *,
        from_rel: Relationships,
        propagation_round: int,
        scenario,
        reset_q: bool = True,
    ) -> None:
        """Full-RIB announcement processing with withdrawal support."""
        from bgpy.simulation_engine.ann_containers import RecvQueue  # noqa: PLC0415

        for prefix, ann_list in policy.recv_q.items():
            local_rib_ann = policy.local_rib.get(prefix)
            og_ann = local_rib_ann

            for new_ann in ann_list:
                assert policy.only_one_withdrawal_per_prefix_per_neighbor(ann_list)
                assert policy.only_one_ann_per_prefix_per_neighbor(ann_list)

                BGPFullExt._process_new_ann_in_ribs_in(
                    policy, new_ann, prefix, from_rel
                )

                if new_ann.withdraw:
                    local_rib_ann = (
                        BGPFullExt._remove_from_local_rib_and_get_new_best_ann(
                            policy, new_ann, local_rib_ann
                        )
                    )
                else:
                    local_rib_ann = policy._get_new_best_ann(  # noqa: SLF001
                        local_rib_ann, new_ann, from_rel
                    )

            if og_ann != local_rib_ann:
                if local_rib_ann:
                    policy.local_rib.add_ann(local_rib_ann)
                if og_ann:
                    BGPFullExt.withdraw_ann_from_neighbors(
                        policy,
                        og_ann.copy(
                            {
                                "next_hop_asn": policy.as_.asn,
                                "withdraw": True,
                            }
                        ),
                    )

        if reset_q:
            policy.recv_q = RecvQueue()

    # -------------------------------------------------------------------------
    # RIBsIn helpers
    # -------------------------------------------------------------------------

    @staticmethod
    def _process_new_ann_in_ribs_in(
        policy: MonoPolicy,
        unprocessed_ann: Ann,
        prefix: str,
        from_rel: Relationships,
    ) -> None:
        """Add or remove from RIBsIn based on whether it's a withdrawal."""
        if unprocessed_ann.withdraw:
            neighbor = unprocessed_ann.as_path[0]
            policy.ribs_in.remove_entry(
                neighbor, prefix, policy.error_on_invalid_routes
            )
        else:
            assert policy.no_implicit_withdrawals(unprocessed_ann, prefix)
            policy.ribs_in.add_unprocessed_ann(unprocessed_ann, from_rel)

    @staticmethod
    def _remove_from_local_rib_and_get_new_best_ann(
        policy: MonoPolicy,
        new_ann: Ann,
        local_rib_ann: Ann | None,
    ) -> Ann | None:
        """Handle withdrawal: remove from local RIB and re-select best."""
        if (
            local_rib_ann
            and new_ann.prefix == local_rib_ann.prefix
            and new_ann.as_path == local_rib_ann.as_path[1:]
            and local_rib_ann.recv_relationship != Relationships.ORIGIN
        ):
            policy.local_rib.pop(new_ann.prefix, None)
            local_rib_ann = None
            processed_best = BGPFullExt._get_and_process_best_ribs_in_ann(
                policy, new_ann.prefix
            )
            if processed_best:
                local_rib_ann = policy._get_best_ann_by_gao_rexford(  # noqa: SLF001
                    local_rib_ann, processed_best
                )
        return local_rib_ann

    @staticmethod
    def _get_and_process_best_ribs_in_ann(
        policy: MonoPolicy, prefix: str
    ) -> Ann | None:
        """Select and process the best unprocessed announcement from RIBsIn."""
        best_ann = None
        for ann_info in policy.ribs_in.get_ann_infos(prefix):
            best_ann = policy._get_new_best_ann(  # noqa: SLF001
                best_ann,
                ann_info.unprocessed_ann,
                ann_info.recv_relationship,
            )
        return best_ann

    # -------------------------------------------------------------------------
    # Propagation helpers
    # -------------------------------------------------------------------------

    @staticmethod
    def withdraw_ann_from_neighbors(
        policy: MonoPolicy, withdraw_ann: Ann
    ) -> None:
        """Withdraw a route from all neighbors that received it."""
        assert withdraw_ann.withdraw is True
        assert withdraw_ann.next_hop_asn == policy.as_.asn
        for send_neighbor_asn in policy.ribs_out.neighbors():
            removed = policy.ribs_out.remove_entry(
                send_neighbor_asn, withdraw_ann.prefix
            )
            if removed:
                send_rels = set(Relationships)
                if send_neighbor_asn in policy.as_.customer_asns:
                    propagate_to = Relationships.CUSTOMERS
                elif send_neighbor_asn in policy.as_.provider_asns:
                    propagate_to = Relationships.PROVIDERS
                elif send_neighbor_asn in policy.as_.peer_asns:
                    propagate_to = Relationships.PEERS
                else:
                    raise NotImplementedError("Case not accounted for")
                send_neighbor = policy.as_.as_graph.as_dict[send_neighbor_asn]
                if policy._policy_propagate(  # noqa: SLF001
                    send_neighbor, withdraw_ann, propagate_to, send_rels
                ):
                    continue
                else:
                    BGPFullExt._process_outgoing_ann(
                        policy, send_neighbor, withdraw_ann, propagate_to, send_rels
                    )

    @staticmethod
    def prev_sent(policy: MonoPolicy, neighbor, ann: Ann) -> bool:
        """Return True if ann was already sent to neighbor (via RIBsOut)."""
        return ann == policy.ribs_out.get_ann(neighbor.asn, ann.prefix)

    @staticmethod
    def _process_outgoing_ann(
        policy: MonoPolicy,
        neighbor,
        ann: Ann,
        propagate_to,
        send_rels,
    ) -> None:
        """Record in RIBsOut, then deliver to neighbor's recv_q."""
        from bgpy.simulation_engine.policies.bgp.bgp.propagate_funcs import (  # noqa: PLC0415
            _process_outgoing_ann as bgp_process_outgoing_ann,
        )

        if not ann.withdraw:
            policy.ribs_out.add_ann(neighbor.asn, ann)
        bgp_process_outgoing_ann(policy, neighbor, ann, propagate_to, send_rels)

    # -------------------------------------------------------------------------
    # Validation helpers (used as assert guards)
    # -------------------------------------------------------------------------

    @staticmethod
    def only_one_withdrawal_per_prefix_per_neighbor(
        policy: MonoPolicy, anns: list[Ann]
    ) -> bool:
        """Ensure at most one withdrawal per prefix per neighbor."""
        assert not (
            len([x.as_path[0] for x in anns if x.withdraw])
            != len({x.as_path[0] for x in anns if x.withdraw})
            and policy.error_on_invalid_routes
        ), f"More than one withdrawal per prefix from the same neighbor {anns}"
        return True

    @staticmethod
    def only_one_ann_per_prefix_per_neighbor(
        policy: MonoPolicy, anns: list[Ann]
    ) -> bool:
        """Ensure at most one non-withdrawal per prefix per neighbor."""
        err = (
            f"{policy.as_.asn} Received two NON withdrawals from "
            f"the same neighbor {anns}"
        )
        assert not (
            len([(x.as_path[0], x.next_hop_asn) for x in anns if not x.withdraw])
            != len(
                {(x.as_path[0], x.next_hop_asn) for x in anns if not x.withdraw}
            )
            and policy.error_on_invalid_routes
        ), err
        return True

    @staticmethod
    def no_implicit_withdrawals(
        policy: MonoPolicy, ann: Ann, prefix: str
    ) -> bool:
        """Ensure no announcement overwrites another without an explicit withdrawal."""
        ribs_in_ann = policy.ribs_in.get_unprocessed_ann_recv_rel(
            ann.as_path[0], prefix
        )
        err = (
            f"Ann {ann} overwrote RIBsIn ann {ribs_in_ann} at AS {policy.as_.asn}. "
            "You must withdraw first, then add new ann"
        )
        assert ribs_in_ann is None or not policy.error_on_invalid_routes, err
        return True
