"""Composition demo: combine policies that have no pre-existing subclass."""

from bgpy.settings import Settings

# This combination has no pre-existing subclass in bgpy
composed = Settings.compose_policy(["ASPA", "Peerlock Lite"])

print(f"Composed class: {composed}")
print(f"\nMRO:")
for cls in composed.__mro__:
    print(f"  {cls.__name__}")

# Calling it again returns the exact same cached class
composed_again = Settings.compose_policy(["ASPA", "Peerlock Lite"])
print(f"\nSame object on repeated call: {composed is composed_again}")

# Full RIB variant
composed_full = Settings.compose_policy(["ASPA", "Peerlock Lite"], full_rib=True)
print(f"\nFull RIB MRO:")
for cls in composed_full.__mro__:
    print(f"  {cls.__name__}")

# Instantiate and confirm ribs_in/ribs_out present on full, absent on lite
instance_lite = composed()
instance_full = composed_full()
print(f"\nLite has ribs_in: {hasattr(instance_lite, 'ribs_in')}")
print(f"Full has ribs_in: {hasattr(instance_full, 'ribs_in')}")
