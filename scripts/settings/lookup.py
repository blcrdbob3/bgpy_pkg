"""Lookup demo: get_policy() returns the exact same class as a direct import."""

from bgpy.settings import Settings
from bgpy.simulation_engine.policies.rov import ROV
from bgpy.simulation_engine.policies.aspa import ASPA

rov_via_settings = Settings.get_policy("ROV")
aspa_via_settings = Settings.get_policy("ASPA")

print(f"Settings.get_policy('ROV') is ROV:  {rov_via_settings is ROV}")
print(f"Settings.get_policy('ASPA') is ASPA: {aspa_via_settings is ASPA}")
print(f"\nROV:  {rov_via_settings}")
print(f"ASPA: {aspa_via_settings}")
