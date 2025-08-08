#!/usr/bin/env python3
"""
Batch update parsers to use gron format for JSON events
"""
import json
import os

def create_gron_parser(product_name, vendor_name, category="security"):
    """Create a gron-based parser template"""
    return {
        "attributes": {
            "dataSource.category": category,
            "dataSource.name": product_name,
            "dataSource.vendor": vendor_name,
            "metadata.product.name": product_name,
            "metadata.product.vendor_name": vendor_name,
            "metadata.version": "1.0.0"
        },
        "formats": [
            {
                "format": "$unmapped.{parse=gron}$",
                "rewrites": [
                    {
                        "input": "unmapped.timestamp",
                        "output": "timestamp",
                        "match": ".*",
                        "replace": "$0"
                    }
                ]
            }
        ],
        "mappings": {
            "version": 1,
            "mappings": [
                {
                    "predicate": "true",
                    "transformations": [
                        {
                            "copy": {
                                "from": "unmapped.timestamp",
                                "to": "time"
                            }
                        },
                        {
                            "cast": {
                                "field": "time",
                                "type": "iso8601TimestampToEpochSec"
                            }
                        }
                    ]
                }
            ]
        }
    }

# Parsers to update with their details
parsers_to_update = {
    "imperva_sonar": {
        "vendor": "Imperva",
        "product": "Sonar",
        "category": "security",
        "path": "parsers/community/imperva_sonar-latest/imperva_sonar.json"
    },
    "isc_bind": {
        "vendor": "ISC",
        "product": "BIND DNS",
        "category": "network",
        "path": "parsers/community/isc_bind-latest/isc_bind.json"
    },
    "isc_dhcp": {
        "vendor": "ISC", 
        "product": "DHCP Server",
        "category": "network",
        "path": "parsers/community/isc_dhcp-latest/isc_dhcp.json"
    },
    "rsa_adaptive": {
        "vendor": "RSA",
        "product": "Adaptive Authentication",
        "category": "security",
        "path": "parsers/community/rsa_adaptive-latest/rsa_adaptive.json"
    },
    "wiz_cloud": {
        "vendor": "Wiz",
        "product": "Cloud Security",
        "category": "security", 
        "path": "parsers/community/wiz_cloud-latest/wiz_cloud.json"
    },
    "cisco_meraki": {
        "vendor": "Cisco",
        "product": "Meraki",
        "category": "network",
        "path": "parsers/community/cisco_meraki-latest/cisco_meraki.json"
    }
}

def main():
    updated_count = 0
    
    for parser_name, details in parsers_to_update.items():
        file_path = f"/Users/nathanial.smalley/projects/jarvis_coding/{details['path']}"
        
        if os.path.exists(file_path):
            # Create new gron parser
            new_parser = create_gron_parser(
                details['product'],
                details['vendor'], 
                details['category']
            )
            
            # Write to file
            with open(file_path, 'w') as f:
                json.dump(new_parser, f, indent=2)
            
            print(f"✅ Updated {parser_name} parser to gron format")
            updated_count += 1
        else:
            print(f"❌ File not found: {file_path}")
    
    print(f"\nUpdated {updated_count} parsers to gron format")
    print("These parsers now handle JSON events with dot notation correctly.")

if __name__ == "__main__":
    main()