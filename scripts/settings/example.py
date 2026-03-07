"""Single-engine run using a composed policy from Settings.

Uses the same topology and scenario structure as scripts/example.py, but
demonstrates Settings.compose_policy (ASPA + Peerlock Lite) as the adopt
policy. Produces a diagram PDF showing ASNs and runs a SubprefixHijack.
"""

from pathlib import Path
from pprint import pprint

from bgpy.shared.enums import ASNs, Prefixes, Relationships, Timestamps
from bgpy.simulation_framework import ScenarioConfig
from bgpy.simulation_framework import SubprefixHijack
from bgpy.simulation_engine import BGP
from bgpy.as_graphs import ASGraphInfo
from bgpy.as_graphs.base.links import CustomerProviderLink as CPLink
from bgpy.as_graphs.base.links import PeerLink
from bgpy.utils import EngineRunConfig, EngineRunner
from bgpy.settings import Settings

TARGET_ASN = 10

# Compose ASPA + Peerlock Lite as the adopt policy
ASPAPeerlockLite = Settings.compose_policy(["ASPA", "Peerlock Lite"])
print(f"Adopt policy: {ASPAPeerlockLite.__name__}")
print(f"MRO: {[c.__name__ for c in ASPAPeerlockLite.__mro__]}\n")

# Same topology as scripts/example.py
as_graph = ASGraphInfo(
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

conf = EngineRunConfig(
    name="Settings example run",
    desc="SubprefixHijack with ASPA + Peerlock Lite",
    scenario_config=ScenarioConfig(
        ScenarioCls=SubprefixHijack,
        BasePolicyCls=BGP,
        AdoptPolicyCls=ASPAPeerlockLite,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
    ),
    as_graph_info=as_graph,
)

runner = EngineRunner(
    conf=conf, base_dir=Path.home() / "Desktop" / "settings_example"
)
(engine, outcomes_yaml, graph_data_aggregator, scenario) = runner.run_engine()

print("Printing each AS")
for asn, as_obj in engine.as_graph.as_dict.items():
    print(f"ASN: {asn}")
    pprint(as_obj.policy.local_rib)

print(f"\nTarget ASN: {TARGET_ASN}")
pprint(engine.as_graph.as_dict[TARGET_ASN].policy.local_rib)
