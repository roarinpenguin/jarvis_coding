# Legacy Files

This folder contains deprecated files that have been superseded by marketplace parsers or better alternatives.

## Deprecated Testing Files
- `comprehensive_field_matcher.py` - Legacy field analysis (replaced by `final_parser_validation.py`)
- `comprehensive_parser_effectiveness_tester.py` - Legacy parser testing (replaced by `final_parser_validation.py`)  
- `end_to_end_pipeline_tester.py` - Legacy pipeline testing (replaced by `final_parser_validation.py`)

## Community Generators Replaced by Marketplace Parsers
- `aws_elb.py` - Replaced by `aws_elasticloadbalancer.py` (marketplace: `marketplace-awselasticloadbalancer-latest`)
- `aws_vpcflow.py` - Replaced by `aws_vpcflowlogs.py` (marketplace: `marketplace-awsvpcflowlogs-latest`)
- `check_point_ngfw.py` - Replaced by `checkpoint.py` (marketplace: `marketplace-checkpointfirewall-latest`)

## Duplicate Generators Consolidated  
- `darktrace_darktrace.py` - Duplicate of `darktrace.py` (kept the more comprehensive version)
- `manageengine_ad_audit_plus.py` - Duplicate of `manageengine_adauditplus.py` (kept the mapped version)

## Why These Were Moved
1. **Marketplace Priority**: We prioritize marketplace parsers over community parsers for better OCSF compliance (15-40% improvement)
2. **Testing Modernization**: New `final_parser_validation.py` provides comprehensive SDL API validation
3. **Reduced Duplication**: Eliminated redundant generators to streamline the codebase
4. **Production Focus**: Marketplace parsers are production-grade with enhanced field extraction

## Recovery
If you need to restore any of these files, they can be moved back from this folder and re-added to `hec_sender.py` mappings.