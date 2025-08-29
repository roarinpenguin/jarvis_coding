#!/usr/bin/env python3
"""
Generator Name Mappings
Maps generator file names to their actual function names
"""

# Mapping of generator file names to their actual log function names
GENERATOR_FUNCTION_MAPPINGS = {
    # AWS generators (remove aws_ prefix)
    "aws_cloudtrail": "cloudtrail_log",
    "aws_guardduty": "guardduty_log", 
    "aws_vpcflowlogs": "vpcflow_log",
    
    # Cisco generators (shortened names)
    "cisco_asa": "asa_log",
    
    # Microsoft (shortened)
    "microsoft_azuread": "azure_ad_log",
    
    # CrowdStrike (shortened)
    "crowdstrike_falcon": "crowdstrike_log",
    
    # Fortinet special case (multiple functions)
    "fortinet_fortigate": "forward_log",  # Use forward_log as default
    
    # Cisco Umbrella (has the function, just needs requests library)
    "cisco_umbrella": "cisco_umbrella_log"
}

def get_log_function_name(generator_name: str) -> str:
    """
    Get the actual log function name for a generator
    
    Args:
        generator_name: The generator file name (without .py)
        
    Returns:
        The actual function name to call
    """
    # Check if there's a special mapping
    if generator_name in GENERATOR_FUNCTION_MAPPINGS:
        return GENERATOR_FUNCTION_MAPPINGS[generator_name]
    
    # Default pattern: add _log suffix
    return f"{generator_name}_log"