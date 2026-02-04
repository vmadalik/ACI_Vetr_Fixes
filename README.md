# ACI Fabric Configuration & Health Check Scripts

A collection of Python scripts for automating Cisco ACI (Application Centric Infrastructure) fabric configuration and implementing security/operational best practices across multiple fabrics.

## Overview

This repository contains scripts designed to configure and harden ACI fabrics according to United Healthcare Group (UHG) standards. All scripts support multi-fabric operations by reading credentials from a CSV file.

## Prerequisites

- Python 3.x
- ACI Fabric running version 5.2(6e) or compatible
- APIC admin access credentials
- Required Python packages (see `requirements.txt`)

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

### Credentials File Format

Create a CSV file named `creds.csv` in the same directory as the scripts with the following format:

```csv
APIC_URL,USERNAME,PASSWORD
https://172.18.97.175,admin,cisco.123
https://apic2.example.com,admin,password2
```

**Note:** Keep credential files secure and never commit them to version control. The `.gitignore` file is configured to exclude all `.csv` files.

### Default Behavior

All scripts now default to using `creds.csv` in the script directory. You can:
- Press Enter to use the default path
- Enter a custom path to use a different credentials file

## Available Scripts

### 1. ACI_DOM.py
**Purpose:** Enable DOM (Digital Optical Monitoring) on fabric nodes

**Features:**
- Prompts for custom policy name
- Lists all fabric leaf node policy groups
- Creates fabric node control policy to enable DOM
- Associates policy to selected policy groups
- Interactive group selection
- Exception handling for duplicate associations

**Usage:**
```bash
python ACI_DOM.py
```

**Workflow:**
1. Enter credentials file path (or use default)
2. Provide custom policy name
3. Login to each fabric
4. Select policy groups from list
5. Confirm policy creation
6. Confirm policy-to-group association

### 2. ACI_MCP.py
**Purpose:** Enable MCP (Mis-Cabling Protocol) Global Instance Policy

**Features:**
- Checks/enables MCP Instance Policy 'default' globally
- Simplified to only handle global fabric policy

**Usage:**
```bash
python ACI_MCP.py
```

**Workflow:**
1. Enter credentials file path (or use default)
2. Login to each fabric
3. Check MCP Instance Policy status
4. Enable if not already enabled

**Note:** Interface policy creation and port group association features are commented out. This script focuses on global MCP enablement only.

### 3. Rogue_EP_Control.py
**Purpose:** Enable Rogue Endpoint Control

**Features:**
- Checks current Rogue EP Control status
- Enables with configurable parameters:
  - Hold Interval: 1800 seconds
  - Detection Interval: 60 seconds
  - Detection Multiplier: 4

**Usage:**
```bash
python Rogue_EP_Control.py
```

### 4. ACI_Port_Tracking.py
**Purpose:** Enable Port Tracking in Global Endpoint Tracking Policy

**Features:**
- Checks if Port Tracking is enabled
- Enables Port Tracking globally
- Default CSV path support

**Usage:**
```bash
python ACI_Port_Tracking.py
```

### 5. ACI_Coopstrict.py
**Purpose:** Enable COOP Strict Mode

**Features:**
- Checks COOP protocol mode
- Enables strict mode for enhanced security
- Compatible with ACI 5.2(6e)
- Default CSV path support

**Usage:**
```bash
python ACI_Coopstrict.py
```

### 6. ACI_Disable_EP_learning.py
**Purpose:** Disable Remote Endpoint Learning

**Features:**
- Checks Remote EP Learning status
- Disables unicast cross-fabric EP learning
- Enhances fabric security
- Default CSV path support

**Usage:**
```bash
python ACI_Disable_EP_learning.py
```

## Common Script Features

All scripts include:
- ✅ Multi-fabric support
- ✅ Interactive user prompts
- ✅ Error handling and logging
- ✅ Pre-configuration state checking
- ✅ Skip/continue options at each step
- ✅ Self-signed certificate handling
- ✅ Default CSV path (`creds.csv` in script directory)
- ✅ File not found error handling

## Script Flow Pattern

```
1. Prompt for CSV path (default: ./creds.csv)
2. Read credentials from CSV with error handling
3. Loop through each fabric
4. Login and obtain authentication token
5. Check current configuration state
6. Prompt user for action
7. Apply configuration (if confirmed)
8. Handle errors gracefully
9. Continue to next fabric
```

## Security Considerations

- **Never commit credential files** - Use `.gitignore` (already configured)
- Credentials are stored in plaintext CSV files - consider using encrypted storage
- SSL certificate verification is disabled for self-signed certs
- All API calls use HTTPS
- Session tokens are used for authentication

## API Endpoints Used

| Endpoint | Purpose |
|----------|---------|
| `/api/aaaLogin.json` | Authentication |
| `/api/mo/uni/fabric/nodecontrol-*` | Fabric node control policies (DOM) |
| `/api/mo/uni/fabric/mcpInstPol-default` | MCP instance policy (global) |
| `/api/mo/uni/infra/epCtrlP-default.json` | Rogue EP Control |
| `/api/mo/uni/infra/trackEqptFabP-default.json` | Port Tracking |
| `/api/mo/uni/infra/settings.json` | Disable Remote EP Learning |
| `/api/mo/uni/fabric/pol-default.json` | COOP Strict Mode |
| `/api/class/fabricLeNodePGrp` | Leaf node policy groups |

## Error Handling

Scripts handle common errors:
- CSV file not found
- Login failures (invalid credentials)
- Network connectivity issues
- Invalid user selections
- Missing policy groups
- API errors
- Duplicate policy associations

## Recent Updates

**Latest Changes:**
- Added `os` module import for dynamic CSV path resolution
- Default CSV path now uses script directory
- Added file not found error handling
- Simplified ACI_MCP.py to only enable global MCP instance policy
- Added custom policy name input for ACI_DOM.py
- Enhanced exception handling for duplicate associations
- Improved user prompts with default values

## File Structure

```
UHG_HC_Settings/
├── ACI_DOM.py                    # Enable DOM on fabric nodes
├── ACI_MCP.py                    # Enable MCP global instance
├── Rogue_EP_Control.py          # Enable Rogue EP Control
├── ACI_Port_Tracking.py         # Enable Port Tracking
├── ACI_Coopstrict.py            # Enable COOP Strict Mode
├── ACI_Disable_EP_learning.py   # Disable Remote EP Learning
├── creds.csv                     # Credentials (not in repo)
├── requirements.txt              # Python dependencies
├── .gitignore                    # Git ignore rules
├── README.md                     # This file
└── Flow_of_Code.md              # Detailed workflow documentation
```

## Contributing

When adding new scripts:
1. Follow the existing pattern for consistency
2. Include comprehensive error handling
3. Add interactive user prompts
4. Add default CSV path support using `os` module
5. Update this README and Flow_of_Code.md
6. Test against multiple fabrics

## Support

For issues or questions, contact the ACI automation team.

## License

Internal use only - United Healthcare Group

---

**Last Updated:** 2024
**Maintained By:** Network Automation Team
