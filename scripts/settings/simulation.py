"""Simulation demo: use a composed policy as the adopt policy in a scenario.

Runs a SubprefixHijack where adopting ASes use ASPA + Peerlock Lite combined,
a combination that has no pre-existing subclass in bgpy.
"""

from pathlib import Path

from bgpy.simulation_framework import Simulation, ScenarioConfig
from bgpy.simulation_framework.scenarios.roa_based_scenarios import SubprefixHijack
from bgpy.simulation_engine import BGP
from bgpy.settings import Settings

# Compose a policy that no pre-existing subclass covers
ASPAPeerlockLite = Settings.compose_policy(["ASPA", "Peerlock Lite"])
print(f"Adopt policy: {ASPAPeerlockLite.__name__}")
print(f"MRO: {[c.__name__ for c in ASPAPeerlockLite.__mro__]}\n")

sim = Simulation(
    percent_adoptions=(0.0, 0.25, 0.5, 0.75, 1.0),
    scenario_configs=(
        ScenarioConfig(
            ScenarioCls=SubprefixHijack,
            AdoptPolicyCls=ASPAPeerlockLite,
            BasePolicyCls=BGP,
        ),
    ),
    output_dir=Path.home() / "Desktop" / "settings_sim",
)
sim.run()
