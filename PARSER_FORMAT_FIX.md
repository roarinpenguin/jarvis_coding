# Parser Format Fix Documentation

## Problem Summary

The parsers are failing because of a **format mismatch**:
- **Generators** send JSON events with dot-notation field names (e.g., `"source.ip": "192.168.1.1"`)
- **Some parsers** expect raw log format and use regex patterns to extract fields
- **Solution**: Parsers need to use `gron` format to parse JSON events

## Root Cause

1. Generators send JSON events to HEC `/event` endpoint
2. These JSON events have flat structure with dot-notation keys
3. Parsers using regex patterns fail because they expect string logs, not JSON
4. The correct parser format for JSON events is `gron` which automatically parses JSON

## Parser Format Types

### ❌ INCORRECT: Regex-based Parser (for raw logs)
```json
{
  "patterns": {
    "timestampPattern": "\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}Z",
    "logPattern": "PingOneMFA\\s+recordedAt=\"([^\"]+)\"..."
  },
  "formats": [{
    "format": "$timestamp=timestampPattern$ $logPattern$"
  }]
}
```

### ✅ CORRECT: Gron-based Parser (for JSON events)
```json
{
  "formats": [{
    "format": "$unmapped.{parse=gron}$",
    "rewrites": [{
      "input": "unmapped.timestamp",
      "output": "timestamp",
      "match": ".*",
      "replace": "$0"
    }]
  }]
}
```

## Key Differences

| Aspect | Regex Parser | Gron Parser |
|--------|-------------|-------------|
| Input Format | Raw string/syslog | JSON |
| Field Access | Regex groups | `unmapped.fieldname` |
| Dot Notation | Not needed | Escape with `\\.` |
| Use Case | Raw logs, CSV | JSON events from HEC |

## Field Mapping in Gron Parsers

When using gron format with dot-notation fields:
```json
{
  "rename": {
    "from": "unmapped.source\\.ip",  // Escape dots with \\. 
    "to": "src_endpoint.ip"
  }
}
```

## Fixed Parsers

✅ **Updated to gron format:**
- `pingprotect-latest/pingprotect.json`
- `pingone_mfa-latest/pingone_mfa.json`
- `pingfederate-latest/pingfederate.json` (already had gron)

## Parsers Still Needing Updates

Based on analysis, these parsers use regex but their generators send JSON:
- `axway_sftp-latest/axway_sftp.json`
- `cohesity_backup-latest/cohesity_backup.json`
- `veeam_backup-latest/veeam_backup.json`

## How to Fix a Parser

1. Replace the `patterns` and `formats` section with gron format:
```json
"formats": [{
  "format": "$unmapped.{parse=gron}$",
  "rewrites": [{
    "input": "unmapped.timestamp",
    "output": "timestamp",
    "match": ".*",
    "replace": "$0"
  }]
}]
```

2. Update field mappings to use `unmapped.` prefix and escape dots:
```json
{
  "rename": {
    "from": "unmapped.actors\\.user\\.id",
    "to": "actor.user.uid"
  }
}
```

3. Use the template at `parsers/PARSER_TEMPLATE.json` as reference

## Testing

After updating a parser:
1. Generate test events: `python event_python_writer/{product}.py`
2. Send via HEC: `python event_python_writer/hec_sender.py --product {product}`
3. Verify parsing in SentinelOne platform

## Important Notes

1. **Don't change generators** - They correctly send JSON with dot notation
2. **Update parsers only** - Switch from regex to gron format
3. **Invalid JSON in parsers** - Many parser files have invalid JSON (missing quotes). These need fixing too.
4. **54 parser files** have invalid JSON syntax that needs fixing separately

## Automation

Use the provided scripts:
- `parsers/fix_parser_format.py` - Identifies parsers needing updates
- `parsers/PARSER_TEMPLATE.json` - Template for creating new gron-based parsers