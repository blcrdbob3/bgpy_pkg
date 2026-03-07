"""Registry-based lookup and composition for BGPy policies.

Provides a stable API for retrieving and combining Policy subclasses by name
without requiring direct imports of individual classes. All existing imports
and subclasses continue to work unchanged.

Usage::

    from bgpy.settings import Settings

    # Lookup
    ROVCls = Settings.get_policy("ROV")

    # Composition
    ASPAPeerlock = Settings.compose_policy(["ASPA", "PeerlockLite"])

    # Full RIB variant
    ASPAPeerlockFull = Settings.compose_policy(["ASPA", "PeerlockLite"], full_rib=True)
"""

from __future__ import annotations

import sys

# Side-effect import: triggers __init_subclass__ registration for all
# Policy subclasses before any lookup is attempted.
import bgpy.simulation_engine  # noqa: F401

from bgpy.simulation_engine.policies.policy import Policy

_cache: dict[tuple[tuple[str, ...], bool], type[Policy]] = {}


class Settings:
    """Lookup and composition API for BGPy Policy subclasses.

    All methods are static. Do not instantiate this class.
    Policy names match each subclass's .name attribute (e.g. "ROV", "ASPA").
    """

    @staticmethod
    def get_policy(name: str) -> type[Policy]:
        """Return the Policy subclass registered under the given name.

        Args:
            name: The Policy subclass's .name attribute (e.g. "ROV", "BGP").

        Raises:
            KeyError: If no Policy is registered under that name.
        """
        try:
            return Policy.name_to_subclass_dict[name]
        except KeyError:
            available = sorted(Policy.name_to_subclass_dict)
            raise KeyError(
                f"No policy named {name!r}. Available: {available}"
            ) from None

    @staticmethod
    def get_policy_names() -> tuple[str, ...]:
        """Return a sorted tuple of all registered Policy names."""
        return tuple(sorted(Policy.name_to_subclass_dict.keys()))

    @staticmethod
    def compose_policy(
        names: list[str] | tuple[str, ...],
        *,
        full_rib: bool = False,
    ) -> type[Policy]:
        """Return a Policy class combining all named policies via multiple inheritance.

        Each policy's _valid_ann() check runs in MRO order because all
        built-in policies call super()._valid_ann() cooperatively.
        Results are cached: the same (names, full_rib) combination always
        returns the same class object.

        Args:
            names: Policy .name attributes in validation-priority order.
            full_rib: If True, BGPFull is appended to the bases to add
                RIBs In, RIBs Out, and withdrawal support.

        Raises:
            KeyError: If any name is not in the registry.
            TypeError: If the resulting MRO is invalid.
        """
        key = (tuple(names), full_rib)
        if key in _cache:
            return _cache[key]

        bases = [Settings.get_policy(n) for n in names]

        if full_rib:
            bgp_full = Policy.name_to_subclass_dict.get("BGP Full")
            if bgp_full and not any(issubclass(b, bgp_full) for b in bases):
                bases.append(bgp_full)

        # __init_subclass__ fires on type() and would overwrite registry
        # entries for any name that bases[0] already holds. Snapshot and
        # restore to keep the registry clean.
        snapshot = {b.name: b for b in bases}
        cls_name = "_".join(n.replace(" ", "_") for n in names)
        cls = type(cls_name, tuple(bases), {})
        Policy.name_to_subclass_dict.update(snapshot)

        # Ensure pickle can find this class: set __module__ to this module
        # and register it in the module's namespace. Without this, ABCMeta
        # may assign __module__ = 'abc', causing PicklingError at runtime.
        cls.__module__ = __name__
        cls.__qualname__ = cls_name
        cls.name = cls_name
        setattr(sys.modules[__name__], cls_name, cls)

        _cache[key] = cls
        return cls
