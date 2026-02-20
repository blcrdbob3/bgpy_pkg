"""Demo 3: Config-driven simulation

Before Settings, ScenarioConfig required direct class references at import time.
Switching policies or scenarios meant editing the import list and the constructor call.

After: the experiment is described as plain data (strings). Settings resolves names
to classes at runtime. Swapping "ROV" to "ASPA" is a one-character config change,
not a code change.
"""

import json

from bgpy.simulation_framework import ScenarioConfig

# --- BEFORE ---
# Each experiment was written as hardcoded class references.
# Changing the adopt policy or scenario required editing imports and the constructor.

from bgpy.simulation_engine import ROV
from bgpy.simulation_framework import SubprefixHijack

scenario_configs_before = (
    ScenarioConfig(ScenarioCls=SubprefixHijack, AdoptPolicyCls=ROV),
)

print("=== BEFORE ===")
print("Hardcoded class references in Python source:")
print(
    "  ScenarioConfig("
    "ScenarioCls=SubprefixHijack, "
    "AdoptPolicyCls=ROV)"
)
for sc in scenario_configs_before:
    print(f"  -> ScenarioCls={sc.ScenarioCls.__name__}, AdoptPolicyCls={sc.AdoptPolicyCls.__name__}")
print()

# --- AFTER ---
# The experiment is described as a JSON config. No imports needed for the
# policy or scenario classes themselves. The same loader handles any combination.

from bgpy.settings import PolicyConfig, Settings

raw_config = json.loads(
    """
    [
        {
            "scenario": "SubprefixHijack",
            "adopt_policy": {"features": ["ROV"], "full_rib": false}
        },
        {
            "scenario": "SubprefixHijack",
            "adopt_policy": {"features": ["ROV", "OnlyToCustomers"], "full_rib": false}
        },
        {
            "scenario": "PrefixHijack",
            "adopt_policy": {"features": ["ASPA"], "full_rib": true}
        }
    ]
    """
)


def build_scenario_config(cfg: dict) -> ScenarioConfig:
    return ScenarioConfig(
        ScenarioCls=Settings.get_scenario(cfg["scenario"]),
        AdoptPolicyCls=Settings.resolve_policy(
            PolicyConfig(
                features=tuple(cfg["adopt_policy"]["features"]),
                full_rib=cfg["adopt_policy"]["full_rib"],
            )
        ),
    )


scenario_configs_after = tuple(build_scenario_config(cfg) for cfg in raw_config)

print("=== AFTER ===")
print("Config-driven: scenario and policy names live in data, not code.")
print()
for sc in scenario_configs_after:
    print(
        f"  ScenarioCls={sc.ScenarioCls.__name__:<20} "
        f"AdoptPolicyCls={sc.AdoptPolicyCls.__name__}"
    )

print()
print("Swap 'ROV' to 'BGPiSec' in the config, no Python source changes required:")
raw_config[0]["adopt_policy"]["features"] = ["BGP-iSec"]
swapped = build_scenario_config(raw_config[0])
print(f"  AdoptPolicyCls is now: {swapped.AdoptPolicyCls.__name__}")
