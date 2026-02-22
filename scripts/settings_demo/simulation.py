"""Demo: Simulation (config-driven)

Before Settings, running a simulation required direct class imports. Changing
the adopt policy or scenario meant editing import statements and constructor
calls throughout the script.

After: the experiment is described as a plain dict (or JSON file). Settings
resolves names to classes at runtime. Swapping "ROV" to "ASPA" is a one-word
config change, not a code change, and the same runner handles any combination.
"""

from pathlib import Path

from frozendict import frozendict

from bgpy.as_graphs import ASGraphInfo
from bgpy.as_graphs.base.links import CustomerProviderLink as CPLink
from bgpy.as_graphs.base.links import PeerLink
from bgpy.shared.enums import ASNs
from bgpy.simulation_framework import ScenarioConfig
from bgpy.utils import EngineRunConfig, EngineRunner

# Shared small topology (same graph used in example.py)
_as_graph_info = ASGraphInfo(
    peer_links=frozenset(
        {
            PeerLink(8, 9),
            PeerLink(9, 10),
            PeerLink(9, 3),
        }
    ),
    customer_provider_links=frozenset(
        [
            CPLink(provider_asn=1, customer_asn=ASNs.ATTACKER.value),
            CPLink(provider_asn=2, customer_asn=ASNs.ATTACKER.value),
            CPLink(provider_asn=2, customer_asn=ASNs.VICTIM.value),
            CPLink(provider_asn=4, customer_asn=ASNs.VICTIM.value),
            CPLink(provider_asn=5, customer_asn=1),
            CPLink(provider_asn=8, customer_asn=1),
            CPLink(provider_asn=8, customer_asn=2),
            CPLink(provider_asn=9, customer_asn=4),
            CPLink(provider_asn=10, customer_asn=ASNs.VICTIM.value),
            CPLink(provider_asn=11, customer_asn=8),
            CPLink(provider_asn=11, customer_asn=9),
            CPLink(provider_asn=11, customer_asn=10),
            CPLink(provider_asn=12, customer_asn=10),
        ]
    ),
)


def run_and_print(scenario_config: ScenarioConfig, run_name: str) -> None:
    """Run a single engine trial and print the local RIB for ASN 10."""
    conf = EngineRunConfig(
        name=run_name,
        desc=f"Config-driven demo: {run_name}",
        scenario_config=scenario_config,
        as_graph_info=_as_graph_info,
    )
    runner = EngineRunner(
        conf=conf,
        base_dir=Path.home() / "Desktop" / "settings_demo" / run_name,
    )
    engine, *_ = runner.run_engine()
    target_asn = 10
    local_rib = engine.as_graph.as_dict[target_asn].policy.local_rib
    print(f"  Local RIB for ASN {target_asn}: {dict(local_rib)}")
    print()


# --- BEFORE ---
# Direct class imports. Changing the adopt policy or scenario requires editing
# imports and the ScenarioConfig constructor call.

from bgpy.simulation_engine import BGP, ROV
from bgpy.simulation_framework import SubprefixHijack

print("=== BEFORE ===")
print("Hardcoded class references; switching the policy means editing Python.")
print()

scenario_config_before = ScenarioConfig(
    ScenarioCls=SubprefixHijack,
    AdoptPolicyCls=ROV,
    BasePolicyCls=BGP,
    override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
    override_victim_asns=frozenset({ASNs.VICTIM.value}),
    hardcoded_asn_cls_dict=frozendict({1: ROV}),
)
print(
    f"  ScenarioCls={SubprefixHijack.__name__}  "
    f"AdoptPolicyCls={ROV.__name__}  "
    f"BasePolicyCls={BGP.__name__}"
)
run_and_print(scenario_config_before, "before_rov")

# --- AFTER ---
# The experiment lives in a plain dict (could be loaded from a JSON file).
# Settings resolves policy and scenario names to classes at runtime.
# No imports change when the config changes.

from bgpy.settings import PolicyConfig, Settings

experiment = {
    "scenario": "SubprefixHijack",
    "adopt_policy": {"features": ["ROV"], "full_rib": False},
    "base_policy": "BGP",
    "hardcoded_asns": {"1": "ROV"},  # could be loaded from a config file
}

print("=== AFTER ===")
print("Config-driven: policy and scenario names are plain strings in a dict.")
print(f"  experiment = {experiment}")
print()


def build_and_run(exp: dict, run_name: str) -> None:
    ScenarioCls = Settings.get_scenario(exp["scenario"])
    AdoptPolicyCls = Settings.resolve_policy(
        PolicyConfig(
            features=tuple(exp["adopt_policy"]["features"]),
            full_rib=exp["adopt_policy"]["full_rib"],
        )
    )
    BasePolicyCls = Settings.get_policy(exp["base_policy"])
    hardcoded = frozendict(
        {int(asn): Settings.get_policy(name) for asn, name in exp["hardcoded_asns"].items()}
    )

    sc = ScenarioConfig(
        ScenarioCls=ScenarioCls,
        AdoptPolicyCls=AdoptPolicyCls,
        BasePolicyCls=BasePolicyCls,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        hardcoded_asn_cls_dict=hardcoded,
    )
    print(
        f"  ScenarioCls={ScenarioCls.__name__}  "
        f"AdoptPolicyCls={AdoptPolicyCls.__name__}  "
        f"BasePolicyCls={BasePolicyCls.__name__}"
    )
    run_and_print(sc, run_name)


build_and_run(experiment, "after_rov")

# Swap "ROV" to "ASPA" with no Python source change, just update the dict:
print("Swap 'ROV' to 'ASPA' by changing one string in the config:")
experiment["adopt_policy"]["features"] = ["ASPA"]
experiment["hardcoded_asns"]["1"] = "ASPA"
print(f"  experiment = {experiment}")
print()
build_and_run(experiment, "after_aspa")
