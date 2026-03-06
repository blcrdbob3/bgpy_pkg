"""PolicySettings IntEnum for MonoPolicy feature flags."""

from enum import IntEnum


class PolicySettings(IntEnum):
    """Index-based flags for MonoPolicy feature dispatch.

    Each value is the index into the MonoPolicy.settings tuple.
    Order matters — BGP_FULL must remain 0.
    """

    BGP_FULL = 0
    ROV = 1
    PEER_ROV = 2
    ASPA = 3
    ASRA = 4
    ASPAWN = 5
    BGPSEC = 6
    BGP_I_SEC_TRANSITIVE = 7
    BGP_I_SEC_OTC = 8
    PROVIDER_CONE_ID = 9
    BGP_I_SEC = 10
    PATH_END = 11
    PEERLOCK_LITE = 12
    EDGE_FILTER = 13
    ENFORCE_FIRST_AS = 14
    ONLY_TO_CUSTOMERS = 15
