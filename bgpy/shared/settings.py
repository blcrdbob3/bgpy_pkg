"""Global settings for BGPy policies.

This module consolidates all policy configuration in one place
for easy access and management.
"""

from typing import TypeAlias

# Individual policy settings type aliases
# Each policy has its own tuple of boolean flags

ROVPolicySettings: TypeAlias = tuple[bool, bool]
"""ROV settings: (rtr_reset, rollback)"""

EnforceFirstASPolicySettings: TypeAlias = tuple[bool]
"""Enforce-First-AS settings: (enabled,)"""

EdgeFilterPolicySettings: TypeAlias = tuple[bool, bool]
"""Edge-Filter settings: (enabled, filter_external_asns)"""

PeerlockLitePolicySettings: TypeAlias = tuple[bool]
"""PeerlockLite settings: (enabled,)"""

OnlyToCustomersPolicySettings: TypeAlias = tuple[bool]
"""Only-To-Customers settings: (enabled,)"""

PathEndPolicySettings: TypeAlias = tuple[bool]
"""Path-End settings: (enabled,)"""

ASPAPolicySettings: TypeAlias = tuple[bool]
"""ASPA settings: (enabled,)"""

RoSTPolicySettings: TypeAlias = tuple[bool]
"""RoST settings: (enabled,)"""

# Combined policy settings tuple
PolicySettings: TypeAlias = tuple[
    ROVPolicySettings,
    EnforceFirstASPolicySettings,
    EdgeFilterPolicySettings,
    PeerlockLitePolicySettings,
    OnlyToCustomersPolicySettings,
    PathEndPolicySettings,
    ASPAPolicySettings,
    RoSTPolicySettings,
]
