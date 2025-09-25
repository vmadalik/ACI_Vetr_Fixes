This repository is a list of scripts that can be used to fix various issues identified by ACI Vetr. 

# 1. MCP issues and assign to policy and groups
# Flow of the code is as follows:
 1. Login to APIC and get a token.
 2. Check if MCP Instance Policy 'default' is enabled in Global Fabric Policies.
 3. If not enabled, prompt user to enable it.
 4. Create an MCP interface policy with a specified name and enable it.
 5. Associate the created policy to one or more Leaf access port policy groups.
 6. (Optional) Associate the policy group to a specific leaf switch (example for leaf 103).

# 2. Enable DOM and assign to policy and groups
# Fabric Policy - Enabling DOM
 Flow of the code is as follows:
 1. Login to APIC and get a token.
 2. List all policy group names in the fabric and prompt user to choose one or more.
 3. Create a fabric node control policy to enable DOM if it doesn't exist.
 4. Associate the created policy to the selected policy groups.
 5. (Optional) Associate the policy group to a specific leaf switch (example for leaf 103).

# 3. Enable Rougue end point control
# Flow of the code is as follows:
 1. Reads a CSV file containing multiple ACI fabric credentials.
 2. Logs into each fabric using the provided credentials.
 3. Checks if Rogue Endpoint Control is enabled in Global Fabric Policies.
 4. If not enabled, prompts the user to enable it.
 5. Enables Rogue Endpoint Control if the user agrees.

# 4. Enable Port tracking.
# Flow of code:
 1. Ensure Port Tracking is enabled in Global Fabric Policies
 2. If not enabled, prompt the user to enable it

# 5. Disable End Point Learning.
# Flow of the code is as follows:
 1. Reads a CSV file containing multiple ACI fabric credentials.
 2. Logs into each fabric using the provided credentials.
 3. Checks if Remote EP Learning is disabled in Global Fabric Policies.
 4. If not disabled, prompts the user to disable it.
 5. Disables Remote EP Learning if the user agrees.