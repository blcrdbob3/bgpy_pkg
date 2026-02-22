"""Demo 2: Composition

Before Settings, combining two policies required writing a named subclass in your
own file and managing the MRO by hand. Every new combination meant a new class.

After: Settings.compose_policy() creates the combined class dynamically. Results
are cached, so the same combination always returns the same class object.
"""

from bgpy.simulation_engine import ROV
from bgpy.simulation_engine.policies.bgp.bgp_full import BGPFull
from bgpy.simulation_engine.policies.enforce_first_as.enforce_first_as import (
    EnforceFirstAS,
)
from bgpy.simulation_engine.policies.only_to_customers import OnlyToCustomers

# --- BEFORE ---
# To run ROV + OnlyToCustomers you wrote a file that looked like this,
# and you needed a new class for every combination you wanted to study.


class ROVAndOTC(ROV, OnlyToCustomers):
    """Hand-written combination. One class per pair of features."""

    pass


print("=== BEFORE ===")
print("Explicit subclass required for every feature combination:")
print("  class ROVAndOTC(ROV, OnlyToCustomers): pass")
print(f"  issubclass(ROVAndOTC, ROV):              {issubclass(ROVAndOTC, ROV)}")
print(f"  issubclass(ROVAndOTC, OnlyToCustomers):  {issubclass(ROVAndOTC, OnlyToCustomers)}")
print()

# --- AFTER ---
from bgpy.settings import Settings

composed = Settings.compose_policy(["ROV", "OnlyToCustomers"])

print("=== AFTER ===")
print("Settings.compose_policy(['ROV', 'OnlyToCustomers']):")
print(f"  issubclass(..., ROV):             {issubclass(composed, ROV)}")
print(f"  issubclass(..., OnlyToCustomers): {issubclass(composed, OnlyToCustomers)}")
print()

print("Same call returns the cached class object:")
same = Settings.compose_policy(["ROV", "OnlyToCustomers"])
print(f"  composed is same: {composed is same}")
print()

print("Full RIB support requires no additional subclass:")
full = Settings.compose_policy(["ROV", "OnlyToCustomers"], full_rib=True)
print(f"  Settings.compose_policy(['ROV', 'OnlyToCustomers'], full_rib=True)")
print(f"  issubclass(..., ROV):             {issubclass(full, ROV)}")
print(f"  issubclass(..., OnlyToCustomers): {issubclass(full, OnlyToCustomers)}")
print(f"  issubclass(..., BGPFull):         {issubclass(full, BGPFull)}")
print()

print("Three-way combination, also no subclass needed:")
triple = Settings.compose_policy(["ROV", "OnlyToCustomers", "Enforce-First-AS"])
print(f"  Settings.compose_policy(['ROV', 'OnlyToCustomers', 'Enforce-First-AS'])")
print(f"  issubclass(..., ROV):              {issubclass(triple, ROV)}")
print(f"  issubclass(..., OnlyToCustomers):  {issubclass(triple, OnlyToCustomers)}")
print(f"  issubclass(..., EnforceFirstAS):   {issubclass(triple, EnforceFirstAS)}")
