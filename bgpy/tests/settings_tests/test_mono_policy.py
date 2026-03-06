"""Tests for MonoPolicy and Settings.to_mono_policy()."""

from __future__ import annotations

import weakref
from unittest.mock import MagicMock

import pytest

from bgpy.settings import Settings
from bgpy.simulation_engine.announcement import Announcement as Ann
from bgpy.simulation_engine.policies.bgp import BGP
from bgpy.simulation_engine.policies.bgp.bgp_full import BGPFull
from bgpy.simulation_engine.policies.mono_policy import MonoPolicy, PolicySettings
from bgpy.simulation_engine.policies.policy import Policy
from bgpy.shared.enums import Relationships


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_ann(**kwargs):
    """Build an Announcement with sensible defaults."""
    defaults = dict(
        prefix="1.0.0.0/8",
        as_path=(2,),
        next_hop_asn=2,
        recv_relationship=Relationships.ORIGIN,
    )
    defaults.update(kwargs)
    return Ann(**defaults)


def _make_mock_as(asn: int, *, provider_asns=(), customer_asns=(), peer_asns=()):
    """Return a minimal mock AS object compatible with MonoPolicy."""
    mock_as = MagicMock()
    mock_as.asn = asn
    mock_as.provider_asns = frozenset(provider_asns)
    mock_as.customer_asns = frozenset(customer_asns)
    mock_as.peer_asns = frozenset(peer_asns)
    mock_as.input_clique = False
    mock_as.stub = False
    mock_as.multihomed = False
    return mock_as


def _make_policy(cls: type[MonoPolicy], asn: int = 1, **as_kwargs) -> MonoPolicy:
    """Instantiate a MonoPolicy subclass with a minimal mock AS attached.

    The mock AS is kept alive by storing it as ``policy._mock_as`` so that the
    weakref proxy remains valid for the lifetime of the policy object.
    """
    policy = cls()
    mock_as = _make_mock_as(asn, **as_kwargs)
    # Keep a strong reference so the proxy stays valid
    policy._mock_as = mock_as  # type: ignore[attr-defined]
    policy.as_ = weakref.proxy(mock_as)
    return policy


# ---------------------------------------------------------------------------
# PolicySettings
# ---------------------------------------------------------------------------


@pytest.mark.unit_tests
class TestPolicySettings:
    def test_length(self) -> None:
        """PolicySettings has 16 entries."""
        assert len(PolicySettings) == 16

    def test_bgp_full_is_zero(self) -> None:
        """BGP_FULL must be 0 so it's the first element of the settings tuple."""
        assert PolicySettings.BGP_FULL == 0

    def test_values_are_sequential(self) -> None:
        """Values 0..15 are all present."""
        vals = {ps.value for ps in PolicySettings}
        assert vals == set(range(16))

    def test_indexing_with_intEnum(self) -> None:
        """A settings tuple can be indexed with IntEnum values."""
        settings = [False] * len(PolicySettings)
        settings[PolicySettings.ROV] = True
        tup = tuple(settings)
        assert tup[PolicySettings.ROV] is True
        assert tup[PolicySettings.ASPA] is False


# ---------------------------------------------------------------------------
# MonoPolicy base class
# ---------------------------------------------------------------------------


@pytest.mark.unit_tests
class TestMonoPolicyBase:
    def test_is_policy_subclass(self) -> None:
        assert issubclass(MonoPolicy, Policy)

    def test_is_bgp_subclass(self) -> None:
        assert issubclass(MonoPolicy, BGP)

    def test_default_settings_all_false(self) -> None:
        assert all(not v for v in MonoPolicy.settings)

    def test_default_settings_length(self) -> None:
        assert len(MonoPolicy.settings) == len(PolicySettings)

    def test_is_mono_policy_marker(self) -> None:
        assert MonoPolicy._IS_MONO_POLICY is True

    def test_name(self) -> None:
        assert MonoPolicy.name == "MonoPolicy"

    def test_registered_in_policy_registry(self) -> None:
        assert "MonoPolicy" in Policy.name_to_subclass_dict

    def test_instantiation_no_bgp_full(self) -> None:
        """Without BGP_FULL, ribs_in/ribs_out are not created."""
        policy = MonoPolicy()
        assert not hasattr(policy, "ribs_in")
        assert not hasattr(policy, "ribs_out")
        assert hasattr(policy, "local_rib")
        assert hasattr(policy, "recv_q")


# ---------------------------------------------------------------------------
# MonoPolicy.from_settings factory
# ---------------------------------------------------------------------------


@pytest.mark.unit_tests
class TestMonoPolicyFromSettings:
    def test_returns_subclass(self) -> None:
        s = [False] * len(PolicySettings)
        s[PolicySettings.ROV] = True
        cls = MonoPolicy.from_settings(tuple(s), name="TestROV")
        assert issubclass(cls, MonoPolicy)

    def test_settings_baked_in(self) -> None:
        s = [False] * len(PolicySettings)
        s[PolicySettings.ROV] = True
        cls = MonoPolicy.from_settings(tuple(s), name="TestROV2")
        assert cls.settings[PolicySettings.ROV] is True
        assert cls.settings[PolicySettings.ASPA] is False

    def test_cached(self) -> None:
        s = tuple([False] * len(PolicySettings))
        cls1 = MonoPolicy.from_settings(s, name="EmptyMono")
        cls2 = MonoPolicy.from_settings(s, name="EmptyMono")
        assert cls1 is cls2

    def test_auto_name_from_flags(self) -> None:
        s = [False] * len(PolicySettings)
        s[PolicySettings.ROV] = True
        s[PolicySettings.ASPA] = True
        cls = MonoPolicy.from_settings(tuple(s))
        assert "ROV" in cls.name
        assert "ASPA" in cls.name

    def test_wrong_length_raises(self) -> None:
        with pytest.raises(ValueError, match="elements"):
            MonoPolicy.from_settings((False, True))

    def test_registered_under_custom_name(self) -> None:
        s = [False] * len(PolicySettings)
        s[PolicySettings.PEERLOCK_LITE] = True
        cls = MonoPolicy.from_settings(tuple(s), name="MonoPeerlockTest")
        assert Policy.name_to_subclass_dict.get("MonoPeerlockTest") is cls

    def test_existing_registry_not_overwritten(self) -> None:
        """Creating a Mono class does not shadow pre-existing registry entries."""
        from bgpy.simulation_engine.policies.rov.rov import ROV

        before = Policy.name_to_subclass_dict.get("ROV")
        s = [False] * len(PolicySettings)
        # Using a unique name that won't collide
        MonoPolicy.from_settings(tuple(s), name="Mono[SAFE_TEST]")
        after = Policy.name_to_subclass_dict.get("ROV")
        assert before is after is ROV

    def test_bgp_full_creates_ribs(self) -> None:
        s = [False] * len(PolicySettings)
        s[PolicySettings.BGP_FULL] = True
        cls = MonoPolicy.from_settings(tuple(s), name="MonoBGPFullTest")
        policy = cls()
        assert hasattr(policy, "ribs_in")
        assert hasattr(policy, "ribs_out")


# ---------------------------------------------------------------------------
# Settings.to_mono_policy factory
# ---------------------------------------------------------------------------


@pytest.mark.unit_tests
@pytest.mark.framework
class TestSettingsToMonoPolicy:
    def test_rov_flag_set(self) -> None:
        cls = Settings.to_mono_policy(["ROV"])
        assert issubclass(cls, MonoPolicy)
        assert cls.settings[PolicySettings.ROV] is True

    def test_bgp_ignored(self) -> None:
        """'BGP' is accepted and silently skipped."""
        cls = Settings.to_mono_policy(["BGP"])
        assert issubclass(cls, MonoPolicy)
        assert all(not v for v in cls.settings)

    def test_full_rib_flag(self) -> None:
        cls = Settings.to_mono_policy(["ROV"], full_rib=True)
        assert cls.settings[PolicySettings.BGP_FULL] is True
        assert cls.settings[PolicySettings.ROV] is True

    def test_unknown_name_raises(self) -> None:
        with pytest.raises(ValueError, match="no MonoPolicy flag"):
            Settings.to_mono_policy(["NoSuchPolicy"])

    def test_cached(self) -> None:
        cls1 = Settings.to_mono_policy(["ASPA"])
        cls2 = Settings.to_mono_policy(["ASPA"])
        assert cls1 is cls2

    def test_multiple_flags(self) -> None:
        cls = Settings.to_mono_policy(["ROV", "ASPA"])
        assert cls.settings[PolicySettings.ROV] is True
        assert cls.settings[PolicySettings.ASPA] is True

    def test_result_is_mono_policy(self) -> None:
        cls = Settings.to_mono_policy(["OnlyToCustomers"])
        assert issubclass(cls, MonoPolicy)

    def test_bgpisec_transitive_flag(self) -> None:
        cls = Settings.to_mono_policy(["BGP-iSec Transitive Only"])
        assert cls.settings[PolicySettings.BGP_I_SEC_TRANSITIVE] is True

    def test_bgpisec_full_flag(self) -> None:
        cls = Settings.to_mono_policy(["BGP-iSec"])
        assert cls.settings[PolicySettings.BGP_I_SEC] is True

    def test_peerlock_lite_flag(self) -> None:
        cls = Settings.to_mono_policy(["Peerlock Lite"])
        assert cls.settings[PolicySettings.PEERLOCK_LITE] is True


# ---------------------------------------------------------------------------
# _valid_ann dispatch — using mocked ROA checker
# ---------------------------------------------------------------------------


@pytest.mark.unit_tests
class TestMonoPolicyValidAnn:
    """Test _valid_ann dispatch by patching ann_is_invalid_by_roa."""

    def _make_rov_policy(self) -> MonoPolicy:
        cls = Settings.to_mono_policy(["ROV"])
        return _make_policy(cls)

    def test_bgp_loop_prevention(self) -> None:
        """BGP base loop check fires even with no flags."""
        policy = _make_policy(MonoPolicy, asn=1)
        # ann with own ASN in path -> loop -> invalid
        ann = _make_ann(as_path=(1, 2), next_hop_asn=2)
        assert policy._valid_ann(ann, Relationships.PROVIDERS) is False

    def test_bgp_as0_prevention(self) -> None:
        """BGP base drops ann with AS 0 in path."""
        policy = _make_policy(MonoPolicy, asn=1)
        ann = _make_ann(as_path=(0, 2), next_hop_asn=0)
        assert policy._valid_ann(ann, Relationships.PROVIDERS) is False

    def test_bgp_valid_ann_passes(self) -> None:
        """Clean ann passes base BGP check."""
        policy = _make_policy(MonoPolicy, asn=1)
        ann = _make_ann(as_path=(2,), next_hop_asn=2)
        assert policy._valid_ann(ann, Relationships.PROVIDERS) is True

    def test_rov_drops_roa_invalid(self) -> None:
        """ROV flag: ROA-invalid ann is dropped."""
        policy = self._make_rov_policy()
        ann = _make_ann(as_path=(2,), next_hop_asn=2)
        # Monkey-patch the checker
        policy.ann_is_invalid_by_roa = lambda a: True
        assert policy._valid_ann(ann, Relationships.PROVIDERS) is False

    def test_rov_passes_roa_valid(self) -> None:
        """ROV flag: ROA-valid ann passes."""
        policy = self._make_rov_policy()
        ann = _make_ann(as_path=(2,), next_hop_asn=2)
        policy.ann_is_invalid_by_roa = lambda a: False
        assert policy._valid_ann(ann, Relationships.PROVIDERS) is True

    def test_edge_filter_drops_stub_with_extra_asns(self) -> None:
        """EdgeFilter drops announcement from stub AS with extra ASNs in path."""
        cls = Settings.to_mono_policy(["EdgeFilter"])
        policy = _make_policy(cls, asn=1)

        # Mock neighbor AS 2 as stub
        neighbor_as = MagicMock()
        neighbor_as.asn = 2
        neighbor_as.stub = True
        neighbor_as.multihomed = False
        policy.as_.as_graph = MagicMock()
        policy.as_.as_graph.as_dict = {2: neighbor_as, 3: MagicMock(asn=3)}

        ann = _make_ann(as_path=(2, 3), next_hop_asn=2)
        assert policy._valid_ann(ann, Relationships.PROVIDERS) is False

    def test_edge_filter_passes_single_as(self) -> None:
        """EdgeFilter allows single-AS path from stub."""
        cls = Settings.to_mono_policy(["EdgeFilter"])
        policy = _make_policy(cls, asn=1)

        neighbor_as = MagicMock()
        neighbor_as.asn = 2
        neighbor_as.stub = True
        neighbor_as.multihomed = False
        policy.as_.as_graph = MagicMock()
        policy.as_.as_graph.as_dict = {2: neighbor_as}

        ann = _make_ann(as_path=(2,), next_hop_asn=2)
        assert policy._valid_ann(ann, Relationships.PROVIDERS) is True

    def test_only_to_customers_valid_ann(self) -> None:
        """OTC flag: drop ann with OTC set when received from peer (wrong OTC ASN)."""
        cls = Settings.to_mono_policy(["OnlyToCustomers"])
        policy = _make_policy(cls, asn=1)

        ann = _make_ann(
            as_path=(2,),
            next_hop_asn=2,
            recv_relationship=Relationships.PEERS,
            only_to_customers=99,  # set by someone else, not the next hop
        )
        assert policy._valid_ann(ann, Relationships.PEERS) is False

    def test_only_to_customers_pass_when_not_set(self) -> None:
        """OTC flag: no OTC attribute -> pass."""
        cls = Settings.to_mono_policy(["OnlyToCustomers"])
        policy = _make_policy(cls, asn=1)

        ann = _make_ann(as_path=(2,), next_hop_asn=2)
        assert policy._valid_ann(ann, Relationships.PROVIDERS) is True


# ---------------------------------------------------------------------------
# BGP_FULL flag
# ---------------------------------------------------------------------------


@pytest.mark.unit_tests
class TestMonoPolicyBGPFull:
    def test_has_ribs_when_full(self) -> None:
        cls = Settings.to_mono_policy([], full_rib=True)
        policy = cls()
        assert hasattr(policy, "ribs_in")
        assert hasattr(policy, "ribs_out")

    def test_no_ribs_without_full(self) -> None:
        cls = Settings.to_mono_policy(["ROV"])
        policy = cls()
        assert not hasattr(policy, "ribs_in")
        assert not hasattr(policy, "ribs_out")

    def test_is_not_bgpfull_subclass(self) -> None:
        """MonoPolicy does NOT inherit BGPFull even with BGP_FULL flag."""
        cls = Settings.to_mono_policy([], full_rib=True)
        assert not issubclass(cls, BGPFull)

    def test_prev_sent_false_without_full(self) -> None:
        policy = _make_policy(MonoPolicy, asn=1)
        neighbor = MagicMock()
        ann = _make_ann(as_path=(2,))
        assert policy._prev_sent(neighbor, ann) is False


# ---------------------------------------------------------------------------
# receive_ann and process_incoming_anns (BGP Lite path)
# ---------------------------------------------------------------------------


@pytest.mark.unit_tests
class TestMonoPolicyProcessIncoming:
    def test_receive_ann_adds_to_recv_q(self) -> None:
        policy = _make_policy(MonoPolicy, asn=1)
        ann = _make_ann(as_path=(2,), next_hop_asn=2)
        policy.receive_ann(ann)
        assert ann in policy.recv_q.get_ann_list("1.0.0.0/8")

    def test_process_incoming_updates_local_rib(self) -> None:
        """Valid ann ends up in local_rib after process_incoming_anns."""
        policy = _make_policy(MonoPolicy, asn=1)
        ann = _make_ann(as_path=(2,), next_hop_asn=2)
        policy.receive_ann(ann)

        scenario = MagicMock()
        policy.process_incoming_anns(
            from_rel=Relationships.PROVIDERS,
            propagation_round=0,
            scenario=scenario,
        )
        assert policy.local_rib.get("1.0.0.0/8") is not None

    def test_invalid_ann_not_in_rib(self) -> None:
        """Ann with loop (own ASN in path) is not added to local_rib."""
        cls = Settings.to_mono_policy(["ROV"])
        policy = _make_policy(cls, asn=2)
        # own ASN = 2, ann as_path includes 2 -> loop
        ann = _make_ann(as_path=(2, 3), next_hop_asn=2)
        policy.receive_ann(ann)

        scenario = MagicMock()
        policy.process_incoming_anns(
            from_rel=Relationships.PROVIDERS,
            propagation_round=0,
            scenario=scenario,
        )
        assert policy.local_rib.get("1.0.0.0/8") is None

    def test_recv_q_reset_after_processing(self) -> None:
        policy = _make_policy(MonoPolicy, asn=1)
        ann = _make_ann(as_path=(2,), next_hop_asn=2)
        policy.receive_ann(ann)

        scenario = MagicMock()
        policy.process_incoming_anns(
            from_rel=Relationships.PROVIDERS,
            propagation_round=0,
            scenario=scenario,
        )
        assert list(policy.recv_q.items()) == []


# ---------------------------------------------------------------------------
# seed_ann
# ---------------------------------------------------------------------------


@pytest.mark.unit_tests
class TestMonoPolicySeedAnn:
    def test_seed_adds_to_local_rib(self) -> None:
        policy = _make_policy(MonoPolicy, asn=1)
        ann = _make_ann(as_path=(1,), next_hop_asn=1)
        policy.seed_ann(ann)
        assert policy.local_rib.get("1.0.0.0/8") is not None

    def test_bgpsec_seed_sets_path(self) -> None:
        """BGPSec flag: seeding origin sets bgpsec_as_path."""
        cls = Settings.to_mono_policy(["BGPsec"])
        policy = _make_policy(cls, asn=1)
        ann = _make_ann(as_path=(1,), next_hop_asn=1)
        policy.seed_ann(ann)
        seeded = policy.local_rib.get("1.0.0.0/8")
        assert seeded is not None
        assert seeded.bgpsec_as_path == (1,)

    def test_no_bgpsec_seed_empty_path(self) -> None:
        """Without BGPSec flag, bgpsec_as_path is empty."""
        policy = _make_policy(MonoPolicy, asn=1)
        ann = _make_ann(as_path=(1,), next_hop_asn=1)
        policy.seed_ann(ann)
        seeded = policy.local_rib.get("1.0.0.0/8")
        assert seeded is not None
        assert seeded.bgpsec_as_path == ()
