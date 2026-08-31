import re
from typing import Dict, Any

def check_rules(show_outputs: str) -> Dict[str, Any]:
    """
    Deterministic rule engine that checks common CLI show outputs
    for known error patterns.
    """
    results = {
        "status": "OK",
        "errors": []
    }
    
    # Check 1: Interface Administratively Down
    if re.search(r'(?i)administratively down', show_outputs):
        results["errors"].append({
            "rule": "interface_admin_down",
            "message": "An interface is administratively down.",
            "severity": "high"
        })
        results["status"] = "ERRORS_DETECTED"
            
    # Check 2: Missing VLAN in Trunk / Not allowed
    if re.search(r'(?i)(not allowed on trunk|vlan.*missing)', show_outputs):
        results["errors"].append({
            "rule": "vlan_trunk_missing",
            "message": "VLAN not allowed or missing on trunk link.",
            "severity": "high"
        })
        results["status"] = "ERRORS_DETECTED"
        
    # Check 3: Missing Overload (NAT)
    if re.search(r'(?i)no \'ip nat inside source list.*overload\'', show_outputs) or \
       re.search(r'(?i)inside interfaces:\s*\(none\)', show_outputs) or \
       re.search(r'(?i)ip nat inside source list \d+ interface \S+(?!.*overload)', show_outputs):
         results["errors"].append({
            "rule": "nat_missing_overload",
            "message": "NAT configuration is missing 'overload' keyword for PAT, or inside interfaces are not defined.",
            "severity": "high"
        })
         results["status"] = "ERRORS_DETECTED"
         
    # Check 4: IP Address overlap / Duplicate IP
    ip_addresses = re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', show_outputs)
    filtered_ips = [ip for ip in ip_addresses if ip not in ("255.255.255.0", "255.255.255.255", "0.0.0.0")]
    has_duplicates = len(filtered_ips) != len(set(filtered_ips))
    
    if re.search(r'(?i)(duplicate address|overlaps with)', show_outputs) or (len(filtered_ips) > 0 and has_duplicates):
         results["errors"].append({
            "rule": "ip_conflict",
            "message": "Duplicate IP address or subnet overlap detected.",
            "severity": "high"
        })
         results["status"] = "ERRORS_DETECTED"

    # Check 5: Wrong wildcard mask (e.g., 255.255.255.0 instead of 0.0.0.255 in ACL/OSPF)
    if re.search(r'(?i)(access-list|network).*\b255\.255\.', show_outputs):
        results["errors"].append({
            "rule": "wrong_wildcard_mask",
            "message": "Possible wrong wildcard mask used (looks like a subnet mask).",
            "severity": "medium"
        })
        results["status"] = "ERRORS_DETECTED"
        
    # Check 6: Gateway mismatch / not set
    gateway_match = re.search(r'(?i)gateway:\s*([\d\.]+).*is\s*([\d\.]+)', show_outputs)
    if gateway_match and gateway_match.group(1) != gateway_match.group(2):
        results["errors"].append({
            "rule": "gateway_mismatch",
            "message": f"Gateway mismatch detected: {gateway_match.group(1)} vs {gateway_match.group(2)}",
            "severity": "high"
        })
        results["status"] = "ERRORS_DETECTED"
    elif re.search(r'(?i)(gateway of last resort is not set|no default gateway)', show_outputs):
        results["errors"].append({
            "rule": "gateway_missing",
            "message": "Default gateway is missing or not set.",
            "severity": "high"
        })
        results["status"] = "ERRORS_DETECTED"
        
    # Check 7: Missing routes (Network not in table)
    if re.search(r'(?i)not in.*table', show_outputs):
        results["errors"].append({
            "rule": "missing_route",
            "message": "Required route or subnet is missing from the routing table.",
            "severity": "high"
        })
        results["status"] = "ERRORS_DETECTED"

    return results

if __name__ == "__main__":
    test_output = "GigabitEthernet0/0.30 is administratively down, line protocol is down\naccess-list 10 permit 192.168.1.0 255.255.255.0"
    print(check_rules(test_output))
