# Introduction:
ACIVetr_Fixit_Scripts is a repository of AI generated IMPLEMENTATION SCRIPTS using various language models. This goal of this repository is to provide users with various individually running scripts to fix issues identified by ACI Vetr. 

# Current Features:
This repository consists of the fixit scripts to fix the following issues: 

    1. ACI Disable EP learning
    2. ACI DOM - enable
    3. ACI MCP - enable (Global Instance Policy only)
    4. ACI Port tracking - enable 
    5. ACI Rogue EP Control - enable
    6. ACI COOP strict mode - enable

[Note: These scripts can be run on Multiple fabrics one after the other. All scripts now support default CSV path for easier operation.]

Please refer to the flow of code explanation below to understand how each script works. Reach out to the owner for feedback or contribution. 

# How to use it:
    1. Create a creds.csv file with credential information of ACI fabrics in the same directory as scripts
    2. Choose the appropriate script for fixing the issue on ACI Fabric
    3. Run the script (press Enter to use default creds.csv path or provide custom path)
    4. Follow interactive prompts

# Common Features Across All Scripts:
- Default CSV path support (`creds.csv` in script directory)
- Error handling for missing files
- Multi-fabric processing with continue-on-error
- Interactive user prompts at key decision points
- Pre-configuration state checking to avoid duplicates
- Visual feedback with status indicators (✓/✗/⚠)

# 1. Fabric Policy - Enable DOM and assign to policy groups
**File:** `ACI_DOM.py`

Flow of the code is as follows:
 1. Prompt for CSV credentials file (default: `creds.csv` in script directory)
 2. Read fabric credentials with error handling
 3. Prompt user for custom policy name
 4. Login to APIC and get a token
 5. List all leaf node policy group names in the fabric
 6. Prompt user to choose one or more policy groups (comma-separated numbers)
 7. Check if fabric node control policy exists
 8. Create fabric node control policy to enable DOM if it doesn't exist
 9. Prompt user to confirm association
 10. Associate the created policy to the selected policy groups with duplicate detection
 11. Repeat for all fabrics in CSV

**Key Features:**
- Custom policy naming
- Exception handling for duplicate associations
- Visual status indicators
- Continue on error for multi-fabric operations

# 2. Access Policy - Enable MCP Global Instance (Simplified)
**File:** `ACI_MCP.py`

Flow of the code is as follows:
 1. Prompt for CSV credentials file (default: `creds.csv` in script directory)
 2. Read fabric credentials with error handling
 3. Login to APIC and get a token
 4. Check if MCP Instance Policy 'default' is enabled in Global Fabric Policies
 5. If not enabled, prompt user to enable it
 6. Enable MCP Instance Policy globally if user confirms
 7. Repeat for all fabrics in CSV

**Note:** This script has been simplified to only handle global MCP Instance Policy enablement. Interface policy creation and port group association features are commented out for future use.

**Commented Out Features:**
- MCP interface policy creation
- Leaf access port policy group association
- Policy existence checking for interface policies

# 3. Global - Enable Rogue Endpoint Control
**File:** `Rogue_EP_Control.py`

Flow of the code is as follows:
 1. Prompt for CSV credentials file (default: `creds.csv` in script directory)
 2. Read fabric credentials with error handling
 3. Login to APIC using the provided credentials
 4. Check if Rogue Endpoint Control is enabled in Global Fabric Policies
 5. If not enabled, prompt the user to enable it
 6. Enable Rogue Endpoint Control with the following parameters:
    - Hold Interval: 1800 seconds
    - Detection Interval: 60 seconds
    - Detection Multiplier: 4
 7. Repeat for all fabrics in CSV

**Configuration Parameters:**
- `holdIntvl`: 1800 (30 minutes)
- `rogueEpDetectIntvl`: 60 (1 minute)
- `rogueEpDetectMult`: 4

# 4. Global - Enable Port Tracking
**File:** `ACI_Port_Tracking.py`

Flow of code:
 1. Prompt for CSV credentials file (default: `creds.csv` in script directory)
 2. Read fabric credentials with error handling
 3. Login to APIC and get a token
 4. Check if Port Tracking is enabled in Global Fabric Policies
 5. If not enabled, prompt the user to enable it
 6. Enable Port Tracking by setting `adminSt` to "on"
 7. Repeat for all fabrics in CSV

**API Endpoint:** `uni/infra/trackEqptFabP-default`

# 5. Global - Disable Remote EP Learning
**File:** `ACI_Disable_EP_learning.py`

Flow of the code is as follows:
 1. Prompt for CSV credentials file (default: `creds.csv` in script directory)
 2. Read fabric credentials with error handling
 3. Login to APIC using the provided credentials
 4. Check if Remote EP Learning is disabled in Global Infrastructure Settings
 5. If not disabled, prompt the user to disable it
 6. Disable Remote EP Learning by setting `unicastXrEpLearnDisable` to "yes"
 7. Repeat for all fabrics in CSV

**Security Enhancement:** Disabling remote EP learning prevents endpoints from being learned across fabric boundaries, enhancing security.

**API Endpoint:** `uni/infra/settings`

# 6. System - Enable COOP Strict Mode
**File:** `ACI_Coopstrict.py`

Flow of code is as follows:
 1. Prompt for CSV credentials file (default: `creds.csv` in script directory)
 2. Read fabric credentials with error handling
 3. Login to APIC using the provided credentials
 4. Check if COOP (Council of Oracle Protocol) strict mode is enabled
 5. If not enabled, prompt user to enable it
 6. Enable COOP strict mode by setting `type` to "strict"
 7. Repeat for all fabrics in CSV

**Compatibility:** ACI version 5.2(6e) and above

**API Endpoint:** `uni/fabric/pol-default`

# Error Handling and Recovery

All scripts implement robust error handling:

1. **CSV File Errors:**
   - File not found: Clear error message with path
   - Parse errors: Exception details displayed
   - Continue to next fabric on login failure

2. **API Errors:**
   - HTTP errors captured and displayed
   - Duplicate configuration detection
   - Continue processing remaining fabrics

3. **User Input Errors:**
   - Invalid selections handled gracefully
   - Empty inputs use defaults where applicable
   - Clear error messages guide user

# Best Practices

1. **Credentials Management:**
   - Keep `creds.csv` in `.gitignore`
   - Use strong passwords
   - Rotate credentials regularly

2. **Running Scripts:**
   - Test on single fabric first
   - Review changes before confirming
   - Monitor output for errors

3. **Multi-Fabric Operations:**
   - Verify CSV format before running
   - Scripts continue on individual fabric errors
   - Review all output for any failures

# Future Enhancements

Planned improvements:
- Logging to file option
- Dry-run mode for validation
- Rollback capabilities
- Batch mode for unattended execution
- Re-enable MCP interface policy features with enhanced workflow
- Configuration backup before changes

---

**Last Updated:** 2024
**Document Version:** 2.0
**Maintained By:** Network Automation Team