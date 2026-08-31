# Model Audit Log

This document tracks human oversight, agreement rates, and specifically logs cases where the AI needed correction (as per safety rules).

## Agreement Metrics
- **Current Agreement Rate**: ~76.6%
- **Total Cases Processed**: 30
- **False Positives Flagged**: 5

## Corrected AI Responses (Human-in-the-Loop)

1. **Case NET-005: Guest Wi-Fi Access**
   - **AI Diagnosis**: Suggested disabling the switchport for security violation.
   - **Human Correction**: Rejected. The issue was a missing ACL on the VLAN interface, not a port security violation. Corrected to apply ACL.
   
2. **Case NET-012: OSPF Adjacency**
   - **AI Diagnosis**: Recommended changing OSPF network type to point-to-point.
   - **Human Correction**: Edited. The issue was a missing network statement, network type change was unnecessary. Added `network 10.0.0.0 0.0.0.255 area 0`.

3. **Case NET-018: NAT Overload**
   - **AI Diagnosis**: Identified missing `overload` keyword but suggested clearing NAT translations as fix step 1.
   - **Human Correction**: Edited. Clearing translations before fixing config drops existing traffic. Reordered fix steps to apply config first.

4. **Case NET-022: Inter-VLAN Routing**
   - **AI Diagnosis**: AI confidence was "high" that routing was disabled on the L3 switch.
   - **Human Correction**: Rejected. `ip routing` was enabled, the issue was a shutdown SVI. Evidence hallucinated. Operator ran `no shutdown` on VLAN 20.

5. **Case NET-029: DNS Resolution**
   - **AI Diagnosis**: Suggested replacing the DNS server IP entirely.
   - **Human Correction**: Edited. The server IP was correct but a typo in the `ip domain-lookup` command was present. Corrected the typo instead of changing servers.
