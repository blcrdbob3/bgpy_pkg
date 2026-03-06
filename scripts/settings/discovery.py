"""Discovery demo: list all policies available via Settings."""

from bgpy.settings import Settings

names = Settings.get_policy_names()
print(f"{len(names)} registered policies:\n")
for name in names:
    print(f"  {name!r}")
