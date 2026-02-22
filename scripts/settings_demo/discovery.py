"""Demo 1: Discovery

Before Settings, finding available policies required reading the source tree or
documentation. There was no runtime API to enumerate what existed.

After: Settings.get_policy_names() and Settings.get_scenario_names() return live,
sorted tuples of every registered name, and get_policy() / get_scenario() retrieve
classes by name without knowing their module paths.
"""

# --- BEFORE ---
# To use a policy you had to know its exact import path. For example:
#
#   from bgpy.simulation_engine.policies.rov.rov import ROV
#   from bgpy.simulation_engine.policies.rov.rov_full import ROVFull
#   from bgpy.simulation_engine.policies.aspa.aspa import ASPA
#   from bgpy.simulation_engine.policies.bgpisec.bgpisec import BGPiSec
#   ...
#
# And there was no way to ask "what policies are available?" at runtime.

print("=== BEFORE ===")
print("No runtime enumeration. Must read source or docs to discover policy names.")
print()

# --- AFTER ---
from bgpy.settings import Settings

print("=== AFTER ===")
print()

all_policy_names = Settings.get_policy_names()
print(f"Settings.get_policy_names()  ({len(all_policy_names)} policies):")
for name in all_policy_names:
    print(f"  {name}")

print()

all_scenario_names = Settings.get_scenario_names()
print(f"Settings.get_scenario_names()  ({len(all_scenario_names)} scenarios):")
for name in all_scenario_names:
    print(f"  {name}")

print()
print("Retrieve a policy by name (no import path needed):")
ROVCls = Settings.get_policy("ROV")
print(f"  Settings.get_policy('ROV')              -> {ROVCls}")

ROVFullCls = Settings.get_policy("ROV", full_rib=True)
print(f"  Settings.get_policy('ROV', full_rib=True) -> {ROVFullCls}")

SubprefixHijackCls = Settings.get_scenario("SubprefixHijack")
print(f"  Settings.get_scenario('SubprefixHijack')  -> {SubprefixHijackCls}")
