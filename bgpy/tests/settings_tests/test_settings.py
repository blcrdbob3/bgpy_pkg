"""Tests for bgpy.settings.Settings"""

import pytest

from bgpy.settings import (
    PolicyConfig,
    PolicyNotFoundError,
    ScenarioNotFoundError,
    Settings,
)
from bgpy.simulation_engine import ASPA, ROV, Policy
from bgpy.simulation_engine.policies.bgp.bgp_full import BGPFull
from bgpy.simulation_engine.policies.only_to_customers import OnlyToCustomers
from bgpy.simulation_engine.policies.rov.rov_full import ROVFull
from bgpy.simulation_framework import PrefixHijack, SubprefixHijack, ValidPrefix
from bgpy.simulation_framework.scenarios.scenario import Scenario


@pytest.mark.framework
@pytest.mark.unit_tests
class TestSettingsPolicyLookup:
    def test_get_policy_bgp(self) -> None:
        """get_policy returns a Policy subclass with .name == 'BGP'"""
        cls = Settings.get_policy("BGP")
        assert issubclass(cls, Policy)
        assert cls.name == "BGP"

    def test_get_policy_rov(self) -> None:
        """get_policy returns ROV for the name 'ROV'"""
        assert Settings.get_policy("ROV") is ROV

    def test_get_policy_aspa(self) -> None:
        """get_policy returns ASPA for the name 'ASPA'"""
        assert Settings.get_policy("ASPA") is ASPA

    def test_get_policy_returns_policy_subclass(self) -> None:
        """Every name in the registry maps to a Policy subclass"""
        for name in Settings.get_policy_names():
            cls = Settings.get_policy(name)
            assert issubclass(cls, Policy)

    def test_get_policy_not_found_raises(self) -> None:
        """get_policy raises PolicyNotFoundError for unknown names"""
        with pytest.raises(PolicyNotFoundError):
            Settings.get_policy("NoSuchPolicy_XYZ")

    def test_get_policy_error_message_contains_name(self) -> None:
        """PolicyNotFoundError message includes the requested name"""
        with pytest.raises(PolicyNotFoundError, match="FakePolicy"):
            Settings.get_policy("FakePolicy")

    def test_get_policy_names_returns_tuple(self) -> None:
        """get_policy_names returns a tuple"""
        assert isinstance(Settings.get_policy_names(), tuple)

    def test_get_policy_names_is_sorted(self) -> None:
        """get_policy_names returns names in sorted order"""
        names = Settings.get_policy_names()
        assert list(names) == sorted(names)

    def test_get_policy_names_contains_known_policies(self) -> None:
        """Known policy names appear in get_policy_names()"""
        names = Settings.get_policy_names()
        assert "BGP" in names
        assert "ROV" in names
        assert "ASPA" in names

    def test_policy_registry_returns_dict(self) -> None:
        """policy_registry() returns a dict"""
        reg = Settings.policy_registry()
        assert isinstance(reg, dict)

    def test_policy_registry_is_copy(self) -> None:
        """policy_registry() returns a copy, not the live dict"""
        reg1 = Settings.policy_registry()
        reg2 = Settings.policy_registry()
        assert reg1 is not reg2

    def test_policy_name_roundtrip(self) -> None:
        """get_policy(name).name == name for all registry entries"""
        for name in Settings.get_policy_names():
            assert Settings.get_policy(name).name == name


@pytest.mark.framework
@pytest.mark.unit_tests
class TestSettingsScenarioLookup:
    def test_get_scenario_subprefix_hijack(self) -> None:
        """get_scenario returns SubprefixHijack for 'SubprefixHijack'"""
        assert Settings.get_scenario("SubprefixHijack") is SubprefixHijack

    def test_get_scenario_prefix_hijack(self) -> None:
        """get_scenario returns PrefixHijack for 'PrefixHijack'"""
        assert Settings.get_scenario("PrefixHijack") is PrefixHijack

    def test_get_scenario_valid_prefix(self) -> None:
        """get_scenario returns ValidPrefix for 'ValidPrefix'"""
        assert Settings.get_scenario("ValidPrefix") is ValidPrefix

    def test_get_scenario_returns_scenario_subclass(self) -> None:
        """Every name in the scenario registry maps to a Scenario subclass"""
        for name in Settings.get_scenario_names():
            cls = Settings.get_scenario(name)
            assert issubclass(cls, Scenario)

    def test_get_scenario_not_found_raises(self) -> None:
        """get_scenario raises ScenarioNotFoundError for unknown names"""
        with pytest.raises(ScenarioNotFoundError):
            Settings.get_scenario("NoSuchScenario_XYZ")

    def test_get_scenario_error_message_contains_name(self) -> None:
        """ScenarioNotFoundError message includes the requested name"""
        with pytest.raises(ScenarioNotFoundError, match="FakeScenario"):
            Settings.get_scenario("FakeScenario")

    def test_get_scenario_names_returns_tuple(self) -> None:
        """get_scenario_names returns a tuple"""
        assert isinstance(Settings.get_scenario_names(), tuple)

    def test_get_scenario_names_is_sorted(self) -> None:
        """get_scenario_names returns names in sorted order"""
        names = Settings.get_scenario_names()
        assert list(names) == sorted(names)

    def test_get_scenario_names_contains_known_scenarios(self) -> None:
        """Known scenario names appear in get_scenario_names()"""
        names = Settings.get_scenario_names()
        assert "SubprefixHijack" in names
        assert "PrefixHijack" in names
        assert "ValidPrefix" in names

    def test_scenario_registry_returns_dict(self) -> None:
        """scenario_registry() returns a dict"""
        reg = Settings.scenario_registry()
        assert isinstance(reg, dict)

    def test_scenario_registry_is_copy(self) -> None:
        """scenario_registry() returns a copy, not the live dict"""
        reg1 = Settings.scenario_registry()
        reg2 = Settings.scenario_registry()
        assert reg1 is not reg2

    def test_scenario_name_roundtrip(self) -> None:
        """get_scenario(name).__name__ == name for all registry entries"""
        for name in Settings.get_scenario_names():
            assert Settings.get_scenario(name).__name__ == name


@pytest.mark.framework
@pytest.mark.unit_tests
class TestSettingsFullRib:
    def test_get_policy_full_rib_rov(self) -> None:
        """get_policy('ROV', full_rib=True) returns ROVFull"""
        assert Settings.get_policy("ROV", full_rib=True) is ROVFull

    def test_get_policy_full_rib_bgp(self) -> None:
        """get_policy('BGP', full_rib=True) returns BGPFull"""
        assert Settings.get_policy("BGP", full_rib=True) is BGPFull

    def test_get_policy_full_rib_false_is_lite(self) -> None:
        """get_policy('ROV', full_rib=False) returns ROV, not ROVFull"""
        assert Settings.get_policy("ROV", full_rib=False) is ROV

    def test_get_policy_full_rib_no_variant_falls_through(self) -> None:
        """get_policy('BGP Full', full_rib=True) returns BGPFull, no double-wrapping"""
        assert Settings.get_policy("BGP Full", full_rib=True) is BGPFull

    def test_get_policy_full_rib_returns_policy_subclass(self) -> None:
        """get_policy with full_rib=True always returns a Policy subclass"""
        cls = Settings.get_policy("ROV", full_rib=True)
        assert issubclass(cls, Policy)


@pytest.mark.framework
@pytest.mark.unit_tests
class TestSettingsCompose:
    def test_compose_single_name(self) -> None:
        """compose_policy(['ROV']) is a Policy subclass with ROV in MRO"""
        cls = Settings.compose_policy(["ROV"])
        assert issubclass(cls, Policy)
        assert issubclass(cls, ROV)

    def test_compose_two_policies(self) -> None:
        """compose_policy(['ROV', 'OnlyToCustomers']) has both in MRO"""
        cls = Settings.compose_policy(["ROV", "OnlyToCustomers"])
        assert issubclass(cls, ROV)
        assert issubclass(cls, OnlyToCustomers)

    def test_compose_cached(self) -> None:
        """Same args to compose_policy return the identical class object"""
        cls1 = Settings.compose_policy(["ROV", "OnlyToCustomers"])
        cls2 = Settings.compose_policy(["ROV", "OnlyToCustomers"])
        assert cls1 is cls2

    def test_compose_full_rib(self) -> None:
        """compose_policy with full_rib=True includes BGPFull in MRO"""
        cls = Settings.compose_policy(["ROV", "OnlyToCustomers"], full_rib=True)
        assert issubclass(cls, BGPFull)

    def test_compose_unknown_name_raises(self) -> None:
        """compose_policy raises PolicyNotFoundError for an unknown name"""
        with pytest.raises(PolicyNotFoundError):
            Settings.compose_policy(["NoSuchPolicy_XYZ"])

    def test_compose_result_is_policy_subclass(self) -> None:
        """compose_policy always returns a Policy subclass"""
        cls = Settings.compose_policy(["ROV", "OnlyToCustomers"])
        assert issubclass(cls, Policy)


@pytest.mark.framework
@pytest.mark.unit_tests
class TestSettingsPolicyConfig:
    def test_policy_config_defaults(self) -> None:
        """PolicyConfig() has features=('BGP',) and full_rib=False"""
        config = PolicyConfig()
        assert config.features == ("BGP",)
        assert config.full_rib is False

    def test_policy_config_empty_features_raises(self) -> None:
        """PolicyConfig(features=()) raises ValueError"""
        with pytest.raises(ValueError, match="at least one"):
            PolicyConfig(features=())

    def test_policy_config_is_hashable(self) -> None:
        """PolicyConfig can be used as a dict key"""
        config = PolicyConfig(features=("ROV",))
        d: dict[PolicyConfig, int] = {config: 1}
        assert d[config] == 1

    def test_resolve_policy_single_feature(self) -> None:
        """PolicyConfig(('ROV',)) resolves to ROV"""
        config = PolicyConfig(features=("ROV",))
        assert Settings.resolve_policy(config) is ROV

    def test_resolve_policy_single_feature_full_rib(self) -> None:
        """PolicyConfig(('ROV',), full_rib=True) resolves to ROVFull"""
        config = PolicyConfig(features=("ROV",), full_rib=True)
        assert Settings.resolve_policy(config) is ROVFull

    def test_resolve_policy_multi_feature(self) -> None:
        """PolicyConfig(('ROV', 'OnlyToCustomers')) resolves with both in MRO"""
        config = PolicyConfig(features=("ROV", "OnlyToCustomers"))
        cls = Settings.resolve_policy(config)
        assert issubclass(cls, Policy)
        assert issubclass(cls, ROV)
        assert issubclass(cls, OnlyToCustomers)
