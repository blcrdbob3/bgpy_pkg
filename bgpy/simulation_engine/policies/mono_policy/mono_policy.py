"""MonoPolicy: a single class with tuple-indexed feature flags.

Composition via flags replaces class hierarchy.  Old subclasses are
unchanged (backwards compatibility maintained).

Usage::

    from bgpy.simulation_engine.policies.mono_policy import MonoPolicy, PolicySettings

    PS = PolicySettings
    settings = [False] * len(PS)
    settings[PS.ROV] = True
    ROVMono = MonoPolicy.from_settings(tuple(settings), name="Mono[ROV]")

Or via the Settings factory::

    from bgpy.settings import Settings
    ROVMono = Settings.to_mono_policy(["ROV"])
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from bgpy.shared.exceptions import GaoRexfordError
from bgpy.simulation_engine.policies.bgp import BGP
from bgpy.simulation_engine.policies.policy import Policy

from .policy_settings import PolicySettings

if TYPE_CHECKING:
    from bgpy.as_graphs import AS
    from bgpy.shared.enums import Relationships
    from bgpy.simulation_engine.announcement import Announcement as Ann
    from bgpy.simulation_framework import Scenario

_PS = PolicySettings

# Cache: (settings_tuple, name) -> class
_mono_cache: dict[tuple[tuple[bool, ...], str], type[MonoPolicy]] = {}

# Default all-False settings tuple
_DEFAULT_SETTINGS: tuple[bool, ...] = tuple(False for _ in _PS)


class MonoPolicy(BGP):
    """Single policy class dispatching to stateless extension classes.

    Class attributes:
        settings: tuple[bool, ...] — one bool per PolicySettings flag.
            All False on the base class; factory-created subclasses have
            their flags baked in.
        name: str — "MonoPolicy" on base; factory sets a descriptive name.
        error_on_invalid_routes: bool — mirrors BGPFull's attribute so
            BGPFullExt validation helpers can access it.
        _IS_MONO_POLICY: bool — duck-typing marker used by extension helpers
            to recognise MonoPolicy instances without importing this module.
    """

    name: str = "MonoPolicy"
    settings: tuple[bool, ...] = _DEFAULT_SETTINGS
    error_on_invalid_routes: bool = True
    _IS_MONO_POLICY: bool = True

    # -------------------------------------------------------------------------
    # __init__
    # -------------------------------------------------------------------------

    def __init__(
        self,
        *args: Any,
        ribs_in=None,
        ribs_out=None,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        if self.__class__.settings[_PS.BGP_FULL]:
            from bgpy.simulation_engine.ann_containers import (  # noqa: PLC0415
                RIBsIn,
                RIBsOut,
            )

            self.ribs_in = ribs_in or RIBsIn()
            self.ribs_out = ribs_out or RIBsOut()

    # -------------------------------------------------------------------------
    # Factory
    # -------------------------------------------------------------------------

    @classmethod
    def from_settings(
        cls,
        settings_tuple: tuple[bool, ...],
        *,
        name: str | None = None,
    ) -> type[MonoPolicy]:
        """Return a MonoPolicy subclass with the given feature flags.

        Results are cached by (settings_tuple, name).

        Args:
            settings_tuple: One bool per PolicySettings value (length must equal
                len(PolicySettings)).
            name: Optional class name. Defaults to "Mono[FLAG1+FLAG2+...]".
        """
        if len(settings_tuple) != len(_PS):
            raise ValueError(
                f"settings_tuple must have {len(_PS)} elements, "
                f"got {len(settings_tuple)}"
            )

        if name is None:
            active = [_PS(i).name for i, v in enumerate(settings_tuple) if v]
            name = f"Mono[{'+'.join(active)}]" if active else "MonoPolicy"

        key = (settings_tuple, name)
        if key in _mono_cache:
            return _mono_cache[key]

        # Snapshot registry entries that __init_subclass__ would overwrite.
        # The new class will register under `name`; if that name already exists
        # in the registry we restore it after creation.
        existing = Policy.name_to_subclass_dict.get(name)

        new_cls: type[MonoPolicy] = type(  # type: ignore[assignment]
            name,
            (cls,),
            {"settings": settings_tuple, "name": name},
        )

        # Restore any pre-existing registry entry that was shadowed.
        if existing is not None:
            Policy.name_to_subclass_dict[name] = existing

        _mono_cache[key] = new_cls
        return new_cls

    # -------------------------------------------------------------------------
    # _valid_ann — priority-ordered dispatch
    # -------------------------------------------------------------------------

    def _valid_ann(self, ann: Ann, recv_rel: Relationships) -> bool:  # type: ignore[override]
        """Validate ann through each enabled feature check in priority order."""
        from bgpy.simulation_engine.policies.bgp.bgp.process_incoming_funcs import (  # noqa: PLC0415
            _valid_ann as bgp_valid_ann,
        )

        from .extensions import (  # noqa: PLC0415
            ASPAExt,
            ASPAwNExt,
            ASRAExt,
            BGPiSecTransitiveExt,
            EdgeFilterExt,
            EnforceFirstASExt,
            OnlyToCustomersExt,
            PathEndExt,
            PeerlockLiteExt,
            PeerROVExt,
            ProviderConeIDExt,
            ROVExt,
        )

        s = self.__class__.settings

        # 1. BGP base (loop prevention + AS 0)
        if not bgp_valid_ann(self, ann, recv_rel):
            return False

        # 2. ROV (needed by BGPSec and all BGPiSec variants too)
        if (
            s[_PS.ROV]
            or s[_PS.BGPSEC]
            or s[_PS.BGP_I_SEC_TRANSITIVE]
            or s[_PS.BGP_I_SEC_OTC]
            or s[_PS.BGP_I_SEC]
        ) and not ROVExt.valid_ann(self, ann, recv_rel):
            return False

        # 3. PeerROV
        if s[_PS.PEER_ROV] and not PeerROVExt.valid_ann(self, ann, recv_rel):
            return False

        # 4. EdgeFilter
        if s[_PS.EDGE_FILTER] and not EdgeFilterExt.valid_ann(self, ann, recv_rel):
            return False

        # 5. EnforceFirstAS
        if s[_PS.ENFORCE_FIRST_AS] and not EnforceFirstASExt.valid_ann(
            self, ann, recv_rel
        ):
            return False

        # 6. PeerlockLite
        if s[_PS.PEERLOCK_LITE] and not PeerlockLiteExt.valid_ann(
            self, ann, recv_rel
        ):
            return False

        # 7. PathEnd
        if s[_PS.PATH_END] and not PathEndExt.valid_ann(self, ann, recv_rel):
            return False

        # 8. OnlyToCustomers (also covers BGP_I_SEC_OTC and BGP_I_SEC)
        if (
            s[_PS.ONLY_TO_CUSTOMERS] or s[_PS.BGP_I_SEC_OTC] or s[_PS.BGP_I_SEC]
        ) and not OnlyToCustomersExt.valid_ann(self, ann, recv_rel):
            return False

        # 9. ASPA/ASPAwN/ASRA — elif chain (each is a superset of the one below)
        if s[_PS.ASRA]:
            if not ASRAExt.valid_ann(self, ann, recv_rel):
                return False
        elif s[_PS.ASPAWN]:
            if not ASPAwNExt.valid_ann(self, ann, recv_rel):
                return False
        elif s[_PS.ASPA] and not ASPAExt.valid_ann(self, ann, recv_rel):
            return False

        # 10. ProviderConeID
        if (
            s[_PS.PROVIDER_CONE_ID] or s[_PS.BGP_I_SEC]
        ) and not ProviderConeIDExt.valid_ann(self, ann, recv_rel):
            return False

        # 11. BGPiSec Transitive signature check
        if (
            s[_PS.BGP_I_SEC_TRANSITIVE] or s[_PS.BGP_I_SEC]
        ) and not BGPiSecTransitiveExt.valid_ann(self, ann, recv_rel):
            return False

        return True

    # -------------------------------------------------------------------------
    # _copy_and_process — kwargs pipeline
    # -------------------------------------------------------------------------

    def _copy_and_process(
        self,
        ann: Ann,
        recv_relationship: Relationships,
        overwrite_default_kwargs: dict[Any, Any] | None = None,
    ) -> Ann:
        """Build ann copy with BGP base kwargs plus BGPSec/BGPiSec path updates."""
        from bgpy.simulation_engine.policies.bgp.bgp.process_incoming_funcs import (  # noqa: PLC0415
            _copy_and_process as bgp_copy_and_process,
        )

        from .extensions import BGPiSecTransitiveExt, BGPSecExt  # noqa: PLC0415

        s = self.__class__.settings

        if overwrite_default_kwargs is None:
            overwrite_default_kwargs = {}

        # BGPiSecTransitive takes priority — always prepends ASN
        if s[_PS.BGP_I_SEC_TRANSITIVE] or s[_PS.BGP_I_SEC]:
            BGPiSecTransitiveExt.update_copy_kwargs(self, ann, overwrite_default_kwargs)
        elif s[_PS.BGPSEC]:
            BGPSecExt.update_copy_kwargs(self, ann, overwrite_default_kwargs)

        return bgp_copy_and_process(
            self, ann, recv_relationship, overwrite_default_kwargs
        )

    # -------------------------------------------------------------------------
    # _policy_propagate — elif chain
    # -------------------------------------------------------------------------

    def _policy_propagate(
        self,
        neighbor: AS,
        ann: Ann,
        propagate_to: Relationships,
        send_rels: set[Relationships],
    ) -> bool:
        """Policy-specific propagation: handle BGPSec/BGPiSec/OTC fields."""
        from bgpy.shared.enums import Relationships  # noqa: PLC0415

        from .extensions import BGPSecExt  # noqa: PLC0415

        s = self.__class__.settings

        # BGPSec (pure) — only when BGPiSec transitive variants are NOT active
        if (
            s[_PS.BGPSEC]
            and not s[_PS.BGP_I_SEC_TRANSITIVE]
            and not s[_PS.BGP_I_SEC_OTC]
            and not s[_PS.BGP_I_SEC]
        ):
            return BGPSecExt.bgpsec_propagate(
                self, neighbor, ann, propagate_to, send_rels
            )

        # BGPiSecTransitive (± OTC)
        elif s[_PS.BGP_I_SEC_TRANSITIVE] or s[_PS.BGP_I_SEC_OTC] or s[_PS.BGP_I_SEC]:
            send_kwargs: dict[str, Any] = {
                "bgpsec_next_asn": neighbor.asn,
                "bgpsec_as_path": ann.bgpsec_as_path,
            }
            if (s[_PS.BGP_I_SEC_OTC] or s[_PS.BGP_I_SEC]) and propagate_to.value in (
                Relationships.CUSTOMERS.value,
                Relationships.PEERS.value,
            ):
                send_kwargs["only_to_customers"] = self.as_.asn
            send_ann = ann.copy(send_kwargs)
            self._process_outgoing_ann(neighbor, send_ann, propagate_to, send_rels)
            return True

        # OnlyToCustomers (standalone)
        elif s[_PS.ONLY_TO_CUSTOMERS]:
            if propagate_to.value in (
                Relationships.CUSTOMERS.value,
                Relationships.PEERS.value,
            ):
                send_ann = ann.copy({"only_to_customers": self.as_.asn})
                self._process_outgoing_ann(neighbor, send_ann, propagate_to, send_rels)
                return True
            return False

        return False

    # -------------------------------------------------------------------------
    # _get_best_ann_by_gao_rexford — insert BGPSec step
    # -------------------------------------------------------------------------

    def _get_best_ann_by_gao_rexford(
        self,
        current_ann: Ann | None,
        new_ann: Ann,
    ) -> Ann:
        """Gao-Rexford with optional BGPSec tiebreaker inserted after AS-path."""
        from .extensions import BGPSecExt  # noqa: PLC0415

        assert new_ann is not None, "New announcement can't be None"

        if current_ann is None:
            return new_ann

        ann = self._get_best_ann_by_local_pref(current_ann, new_ann)
        if ann:
            return ann

        ann = self._get_best_ann_by_as_path(current_ann, new_ann)
        if ann:
            return ann

        s = self.__class__.settings
        # BGPiSecTransitive disables the BGPSec path preference
        if (
            s[_PS.BGPSEC]
            and not s[_PS.BGP_I_SEC_TRANSITIVE]
            and not s[_PS.BGP_I_SEC]
        ):
            ann = BGPSecExt.get_best_ann_by_bgpsec(self, current_ann, new_ann)
            if ann:
                return ann

        return self._get_best_ann_by_lowest_neighbor_asn_tiebreaker(
            current_ann, new_ann
        )

        raise GaoRexfordError("No ann was chosen")  # type: ignore[unreachable]

    # -------------------------------------------------------------------------
    # process_incoming_anns
    # -------------------------------------------------------------------------

    def process_incoming_anns(
        self,
        *,
        from_rel: Relationships,
        propagation_round: int,
        scenario: Scenario,
        reset_q: bool = True,
    ) -> None:
        """Full-RIB processing when BGP_FULL is set; standard BGP otherwise."""
        if self.__class__.settings[_PS.BGP_FULL]:
            from .extensions import BGPFullExt  # noqa: PLC0415

            BGPFullExt.process_incoming_anns(
                self,
                from_rel=from_rel,
                propagation_round=propagation_round,
                scenario=scenario,
                reset_q=reset_q,
            )
        else:
            from bgpy.simulation_engine.policies.bgp.bgp.process_incoming_funcs import (  # noqa: PLC0415
                process_incoming_anns as bgp_process_incoming_anns,
            )

            bgp_process_incoming_anns(
                self,
                from_rel=from_rel,
                propagation_round=propagation_round,
                scenario=scenario,
                reset_q=reset_q,
            )

    # -------------------------------------------------------------------------
    # seed_ann
    # -------------------------------------------------------------------------

    def seed_ann(self, ann: Ann) -> None:
        """Seed announcement; initialize BGPSec path if BGPSEC is set."""
        from bgpy.simulation_engine.policies.bgp.bgp.process_incoming_funcs import (  # noqa: PLC0415
            seed_ann as bgp_seed_ann,
        )

        from .extensions import BGPSecExt  # noqa: PLC0415

        if self.__class__.settings[_PS.BGPSEC]:
            ann = BGPSecExt.prepare_seed_ann(self, ann)
        bgp_seed_ann(self, ann)

    # -------------------------------------------------------------------------
    # BGP_FULL delegated methods
    # -------------------------------------------------------------------------

    def _prev_sent(self, neighbor: AS, ann: Ann) -> bool:
        if self.__class__.settings[_PS.BGP_FULL]:
            from .extensions import BGPFullExt  # noqa: PLC0415

            return BGPFullExt.prev_sent(self, neighbor, ann)
        return False

    def _process_outgoing_ann(
        self,
        neighbor: AS,
        ann: Ann,
        propagate_to: Relationships,
        send_rels: set[Relationships],
    ) -> None:
        if self.__class__.settings[_PS.BGP_FULL]:
            from .extensions import BGPFullExt  # noqa: PLC0415

            BGPFullExt._process_outgoing_ann(  # noqa: SLF001
                self, neighbor, ann, propagate_to, send_rels
            )
        else:
            from bgpy.simulation_engine.policies.bgp.bgp.propagate_funcs import (  # noqa: PLC0415
                _process_outgoing_ann as bgp_process_outgoing_ann,
            )

            bgp_process_outgoing_ann(self, neighbor, ann, propagate_to, send_rels)

    def withdraw_ann_from_neighbors(self, withdraw_ann: Ann) -> None:
        if self.__class__.settings[_PS.BGP_FULL]:
            from .extensions import BGPFullExt  # noqa: PLC0415

            BGPFullExt.withdraw_ann_from_neighbors(self, withdraw_ann)
        # No-op for non-Full — BGP base doesn't support withdrawals

    # -------------------------------------------------------------------------
    # BGPFull validation helpers (needed by BGPFullExt)
    # -------------------------------------------------------------------------

    def only_one_withdrawal_per_prefix_per_neighbor(
        self, anns: list[Ann]
    ) -> bool:
        from .extensions import BGPFullExt  # noqa: PLC0415

        return BGPFullExt.only_one_withdrawal_per_prefix_per_neighbor(self, anns)

    def only_one_ann_per_prefix_per_neighbor(self, anns: list[Ann]) -> bool:
        from .extensions import BGPFullExt  # noqa: PLC0415

        return BGPFullExt.only_one_ann_per_prefix_per_neighbor(self, anns)

    def no_implicit_withdrawals(self, ann: Ann, prefix: str) -> bool:
        from .extensions import BGPFullExt  # noqa: PLC0415

        return BGPFullExt.no_implicit_withdrawals(self, ann, prefix)

    # -------------------------------------------------------------------------
    # YAML
    # -------------------------------------------------------------------------

    def __to_yaml_dict__(self) -> dict[Any, Any]:
        d: dict[Any, Any] = {"local_rib": self.local_rib, "recv_q": self.recv_q}
        if self.__class__.settings[_PS.BGP_FULL]:
            d.update({"ribs_in": self.ribs_in, "ribs_out": self.ribs_out})
        return d
