"""Registry-based lookup class for BGPy policies and scenarios.

Provides a stable, discoverable API for retrieving Policy and Scenario
subclasses by name without requiring direct imports of every individual class.
Old code using Policy subclasses directly (e.g. ROV, BGP) continues to work
unchanged; Settings is a new alternative API.

Usage:
    from bgpy.settings import Settings

    PolicyCls = Settings.get_policy("ROV")
    ScenarioCls = Settings.get_scenario("SubprefixHijack")
    print(Settings.get_policy_names())
    print(Settings.get_scenario_names())

Note on user-defined Scenario subclasses: if you define a Scenario subclass
after this module is first imported, it will not appear in the scenario
registry. Policy subclasses are always auto-included because Policy uses
__init_subclass__ to maintain a live registry.
"""

from __future__ import annotations

from dataclasses import dataclass

# Bare imports below are side-effect-only: they trigger __init_subclass__
# registration for all Policy and Scenario subclasses before any lookup.
# bgpy.simulation_engine brings in all 60+ policy classes;
# bgpy.simulation_framework.scenarios brings in all built-in scenario classes.
import bgpy.simulation_engine
import bgpy.simulation_framework.scenarios  # noqa: F401
from bgpy.simulation_engine.policies.policy import Policy
from bgpy.simulation_framework.scenarios.scenario import Scenario


class PolicyNotFoundError(KeyError):
    """Raised when a Policy name is not found in the registry."""

    pass


class ScenarioNotFoundError(KeyError):
    """Raised when a Scenario name is not found in the registry."""

    pass


def _build_scenario_name_map() -> dict[str, type[Scenario]]:
    """Build a name-to-class map for all Scenario subclasses.

    Walks the full subclass tree of Scenario via BFS, keyed by each
    class's __name__. Called once at module import time after all
    scenario imports have completed.
    """
    result: dict[str, type[Scenario]] = {}
    queue: list[type[Scenario]] = list(Scenario.__subclasses__())
    while queue:
        cls = queue.pop()
        result[cls.__name__] = cls
        queue.extend(cls.__subclasses__())
    return result


_scenario_name_map: dict[str, type[Scenario]] = _build_scenario_name_map()

_FULL_SUFFIX: str = " Full"


def _build_lite_to_full_map() -> dict[str, str]:
    """Map each Lite policy name to its Full variant name, where a pair exists.

    Relies on the convention that Full variants are named by appending ' Full'
    to the Lite name (e.g., 'ROV' -> 'ROV Full', 'BGP' -> 'BGP Full').
    """
    names = set(Policy.name_to_subclass_dict.keys())
    result: dict[str, str] = {}
    for name in names:
        full_name = name + _FULL_SUFFIX
        if full_name in names:
            result[name] = full_name
    return result


_lite_to_full_map: dict[str, str] = _build_lite_to_full_map()

_compose_cache: dict[tuple[tuple[str, ...], bool], type[Policy]] = {}


@dataclass(frozen=True)
class PolicyConfig:
    """Serializable specification for a Policy class selection or composition.

    Use Settings.resolve_policy(config) to obtain a concrete Policy subclass.

    Attributes:
        features: Tuple of Policy .name attributes, in validation-priority order.
            A single-element tuple returns that policy directly via get_policy().
        full_rib: Whether to include BGPFull (RIBs In, RIBs Out, withdrawals).
    """

    features: tuple[str, ...] = ("BGP",)
    full_rib: bool = False

    def __post_init__(self) -> None:
        if not self.features:
            raise ValueError("features must contain at least one policy name")


class Settings:
    """Registry/lookup class for BGPy Policy and Scenario subclasses.

    All methods are static. Do not instantiate this class.

    Policy names match each Policy subclass's .name class attribute
    (e.g., "ROV", "BGP", "ASPA"). Scenario names match each Scenario
    subclass's Python class name (e.g., "SubprefixHijack").
    """

    @staticmethod
    def get_policy(name: str, *, full_rib: bool = False) -> type[Policy]:
        """Return the Policy subclass registered under the given name.

        Args:
            name: The Policy subclass's .name attribute (e.g., "ROV", "BGP").
            full_rib: If True, return the Full variant (e.g., "ROV Full" for
                "ROV") when one exists. If no Full variant exists for the
                given name, the name is looked up as-is.

        Raises:
            PolicyNotFoundError: If no Policy is registered under name.
        """
        if full_rib:
            full_name = _lite_to_full_map.get(name)
            if full_name is not None:
                name = full_name
        try:
            return Policy.name_to_subclass_dict[name]
        except KeyError:
            available = sorted(Policy.name_to_subclass_dict.keys())
            raise PolicyNotFoundError(
                f"No Policy registered with name {name!r}. "
                f"Use Settings.get_policy_names() to see available names. "
                f"Available: {available}"
            ) from None

    @staticmethod
    def compose_policy(
        names: list[str] | tuple[str, ...],
        *,
        full_rib: bool = False,
    ) -> type[Policy]:
        """Return a Policy class that combines all named policies.

        Dynamically creates a new class via multiple inheritance. Each policy's
        _valid_ann() check runs in MRO order because all built-in policies call
        super()._valid_ann() cooperatively.

        Results are cached: the same (names, full_rib) combination always
        returns the same class object.

        Args:
            names: Policy .name attributes in validation-priority order.
            full_rib: If True, BGPFull is appended to the bases (unless
                already present via inheritance) to add RIBs In, RIBs Out,
                and withdrawal support.

        Raises:
            PolicyNotFoundError: If any name is not in the registry.
            TypeError: If the resulting MRO is invalid (conflicting bases).
        """
        key = (tuple(names), full_rib)
        if key in _compose_cache:
            return _compose_cache[key]

        bases: list[type[Policy]] = [Settings.get_policy(n) for n in names]

        if full_rib:
            bgp_full = Policy.name_to_subclass_dict.get("BGP Full")
            if bgp_full is not None:
                already_has_full = any(issubclass(b, bgp_full) for b in bases)
                if not already_has_full:
                    bases.append(bgp_full)

        composed_name = "_".join(n.replace(" ", "_") for n in names)
        if full_rib:
            composed_name += "_Full"

        # Snapshot the registry entries that __init_subclass__ will overwrite.
        # The composed class inherits .name from bases[0], so creating it via
        # type() will register it under that name, shadowing the real class.
        # We restore the snapshot immediately after to keep the registry clean.
        registry_snapshot = {b.name: b for b in bases}

        try:
            cls = type(composed_name, tuple(bases), {})
        except TypeError as exc:
            raise TypeError(
                f"Cannot compose policies {list(names)!r}: MRO conflict. "
                f"Original error: {exc}"
            ) from exc

        # Restore any registry entries that were overwritten by __init_subclass__
        Policy.name_to_subclass_dict.update(registry_snapshot)

        _compose_cache[key] = cls
        return cls

    @staticmethod
    def resolve_policy(config: PolicyConfig) -> type[Policy]:
        """Return the Policy class described by a PolicyConfig.

        For single-feature configs, delegates to get_policy() and returns the
        exact registered class. For multi-feature configs, delegates to
        compose_policy() and returns a dynamically created class.

        Args:
            config: A PolicyConfig specifying features and RIB depth.

        Raises:
            PolicyNotFoundError: If any feature name in config is not
                registered.
            TypeError: If the combination produces an MRO conflict.
        """
        if len(config.features) == 1:
            return Settings.get_policy(config.features[0], full_rib=config.full_rib)
        return Settings.compose_policy(config.features, full_rib=config.full_rib)

    @staticmethod
    def get_policy_names() -> tuple[str, ...]:
        """Return a sorted tuple of all registered Policy names."""
        return tuple(sorted(Policy.name_to_subclass_dict.keys()))

    @staticmethod
    def policy_registry() -> dict[str, type[Policy]]:
        """Return a copy of the full policy name-to-class registry."""
        return dict(Policy.name_to_subclass_dict)

    @staticmethod
    def get_scenario(name: str) -> type[Scenario]:
        """Return the Scenario subclass with the given class name.

        Args:
            name: The Scenario subclass's Python class name
                (e.g., "SubprefixHijack", "PrefixHijack").

        Raises:
            ScenarioNotFoundError: If no Scenario subclass has that name.
        """
        try:
            return _scenario_name_map[name]
        except KeyError:
            available = sorted(_scenario_name_map.keys())
            raise ScenarioNotFoundError(
                f"No Scenario subclass named {name!r}. "
                f"Use Settings.get_scenario_names() to see available names. "
                f"Available: {available}"
            ) from None

    @staticmethod
    def get_scenario_names() -> tuple[str, ...]:
        """Return a sorted tuple of all known Scenario subclass names."""
        return tuple(sorted(_scenario_name_map.keys()))

    @staticmethod
    def scenario_registry() -> dict[str, type[Scenario]]:
        """Return a copy of the full scenario name-to-class registry."""
        return dict(_scenario_name_map)
