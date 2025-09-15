# Parser Management Migration Guide

## 🔄 Transitioning from Old to New Parser Management

This guide explains the transition from the old `create_sentinelone_parsers.py` approach to the new `download_sentinelone_parsers.py` method.

---

## Old Approach: `create_sentinelone_parsers.py`

### How It Worked:
1. **Required a source JSON file** (`sentinelone_parsers.json`) containing all parser definitions
2. **Manually parsed** the JSON to extract individual parsers
3. **Created directories** locally based on parser names
4. **Fixed JSON syntax** issues in parser configurations
5. **Generated metadata.yaml** files for each parser

### Limitations:
- ❌ Required maintaining a large JSON file locally
- ❌ No automatic updates from official sources
- ❌ Manual process to get new parsers
- ❌ Prone to JSON syntax errors
- ❌ No version tracking

### Old Workflow:
```bash
# 1. You needed a sentinelone_parsers.json file (which you had to obtain somehow)
# 2. Run the script
python utilities/create_sentinelone_parsers.py

# 3. Script would look for these files:
#    - sentinelone_parsers.json
#    - utilities/sentinelone_parsers.json
#    - sentinelone_parsers_example.json
```

---

## New Approach: `download_sentinelone_parsers.py`

### How It Works:
1. **Connects directly to GitHub** repository (https://github.com/Sentinel-One/ai-siem)
2. **Downloads latest parsers** via GitHub API
3. **Automatically organizes** into proper directory structure
4. **Creates inventory** of all downloaded parsers
5. **Handles both** community and marketplace parsers

### Advantages:
- ✅ Always gets latest parser versions
- ✅ No manual file management
- ✅ Direct from official SentinelOne repository
- ✅ Automatic organization
- ✅ Version tracking via inventory
- ✅ Can list without downloading

### New Workflow:
```bash
# 1. List available parsers (no download)
python utilities/download_sentinelone_parsers.py --list

# 2. Download all parsers
python utilities/download_sentinelone_parsers.py

# 3. Parsers are automatically organized:
#    - parsers/community_new/     (148 parsers)
#    - parsers/sentinelone_new/   (17 parsers)
#    - parsers/parser_inventory.json
```

---

## 🔑 Key Differences

| Aspect | Old Method | New Method |
|--------|------------|------------|
| **Source** | Local JSON file | GitHub repository |
| **Updates** | Manual | Automatic |
| **Parser Count** | Limited to what's in JSON | All 165 official parsers |
| **Maintenance** | High - need to maintain JSON | Low - direct from source |
| **Error Handling** | JSON syntax fixes needed | Clean downloads |
| **Version Tracking** | None | Inventory with timestamps |
| **Preview** | No | `--list` flag to preview |

---

## 📝 Migration Steps

### If You Were Using the Old Method:

1. **Check existing parsers:**
   ```bash
   ls parsers/sentinelone/
   ```

2. **List available parsers from GitHub:**
   ```bash
   python utilities/download_sentinelone_parsers.py --list
   ```
   This shows what's available without downloading.

3. **Download new parsers:**
   ```bash
   python utilities/download_sentinelone_parsers.py
   ```
   Downloads to `parsers/community_new/` and `parsers/sentinelone_new/`

4. **Compare and merge:**
   ```bash
   # Compare what you have vs what was downloaded
   diff -r parsers/community parsers/community_new
   diff -r parsers/sentinelone parsers/sentinelone_new
   ```

5. **Update if needed:**
   ```bash
   # Backup existing
   mv parsers/community parsers/community_backup
   mv parsers/sentinelone parsers/sentinelone_backup
   
   # Use new ones
   mv parsers/community_new parsers/community
   mv parsers/sentinelone_new parsers/sentinelone
   ```

---

## 🆚 When to Use Which Script

### Use `create_sentinelone_parsers.py` when:
- You have a custom JSON file with parser definitions
- You need to create parsers from a specific format
- You're working offline without GitHub access
- You have proprietary parser definitions

### Use `download_sentinelone_parsers.py` when:
- You want the latest official parsers
- You need to update existing parsers
- You want to see what's available
- You're setting up a new environment
- You want automatic organization

---

## 📊 Current Parser Status

```
Your Project:
├── parsers/
│   ├── community/          # 116 existing parsers
│   └── sentinelone/        # 18 existing parsers

GitHub Repository:
├── parsers/
│   ├── community/          # 148 available parsers
│   └── sentinelone/        # 17 available parsers
```

**Gap Analysis:**
- Community: You have 116, GitHub has 148 (32 new available)
- SentinelOne: You have 18, GitHub has 17 (you have 1 extra)

---

## 🚀 Quick Start for New Users

If you're starting fresh:

```bash
# 1. Go to utilities directory
cd utilities/

# 2. See what's available
python download_sentinelone_parsers.py --list

# 3. Download everything
python download_sentinelone_parsers.py

# 4. Move to correct location
mv parsers/community_new ../parsers/community
mv parsers/sentinelone_new ../parsers/sentinelone

# 5. Verify
ls ../parsers/community | wc -l   # Should show 148
ls ../parsers/sentinelone | wc -l  # Should show 17
```

---

## ⚠️ Important Notes

1. **The old script still works** - If you have custom parser JSON files, `create_sentinelone_parsers.py` is still functional
2. **No data loss** - The new script downloads to `_new` directories, so existing parsers are safe
3. **GitHub API limits** - If downloading many files, you might hit rate limits. Wait and retry.
4. **Network required** - The new method requires internet access to GitHub

---

## 📋 Example Parser Structure

Both methods create the same structure:

```
parsers/community/aws_cloudtrail-latest/
├── aws_cloudtrail.conf       # Parser configuration
└── metadata.yaml             # Parser metadata

parsers/sentinelone/marketplace-fortinetfortigate-latest/
├── marketplace-fortinetfortigate-latest.json  # Parser config
└── metadata.yaml                               # Parser metadata
```

---

## 🤝 Support

- **Issues with downloading?** Check network and GitHub API status
- **JSON syntax errors?** Use the old script with `sentinelone_parsers_example.json`
- **Missing parsers?** Compare inventory with GitHub repository
- **Need specific parsers?** Can still use targeted downloads or old method