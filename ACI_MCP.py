##################
# Access Policy -- Enabling MCP
# Flow of the code is as follows:
# 1. Login to APIC and get a token.
# 2. Check if MCP Instance Policy 'default' is enabled in Global Fabric Policies.
# 3. If not enabled, prompt user to enable it.
# 4. Create an MCP interface policy with a specified name and enable it.
# 5. Associate the created policy to one or more Leaf access port policy groups.
# 6. (Optional) Associate the policy group to a specific leaf switch (example for leaf 103).
###################


import requests
import urllib3
import csv

# Disable warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

policy_name = "MCP-Interface-Policy_Vishwa"

def read_fabric_credentials(csv_path):
    fabrics = []
    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            fabrics.append({
                "APIC_URL": row["APIC_URL"],
                "USERNAME": row["USERNAME"],
                "PASSWORD": row["PASSWORD"]
            })
    return fabrics

def login(APIC_URL, USERNAME, PASSWORD):
    url = f"{APIC_URL}/api/aaaLogin.json"
    payload = {
        "aaaUser": {
            "attributes": {
                "name": USERNAME,
                "pwd": PASSWORD
            }
        }
    }
    response = requests.post(url, json=payload, verify=False)
    response.raise_for_status()
    token = response.json()['imdata'][0]['aaaLogin']['attributes']['token']
    return token

def ensure_mcp_instance_policy_enabled(APIC_URL, token):
    url = f"{APIC_URL}/api/mo/uni/infra/mcpInstP-default.json"
    headers = {"Cookie": f"APIC-cookie={token}"}
    response = requests.get(url, headers=headers, verify=False)
    response.raise_for_status()
    data = response.json()
    enabled = False
    if data.get('imdata'):
        attrs = data['imdata'][0]['mcpInstPol']['attributes']
        if attrs.get('adminSt', '').lower() == 'enabled':
            enabled = True
    if not enabled:
        print("WARNING: MCP Instance Policy 'default' is not enabled in Global Fabric Policies.")
        choice = input("Do you want to enable MCP Instance Policy 'default'? (y/n): ")
        if choice.strip().lower() == 'y':
            payload = {
                "mcpInstPol": {
                    "attributes": {
                        "dn": "uni/fabric/mcpInstPol-default",
                        "name": "default",
                        "adminSt": "enabled",
                        "status": "modified"
                    }
                }
            }
            post_url = f"{APIC_URL}/api/mo/uni/fabric/mcpInstPol-default.json"
            post_response = requests.post(post_url, json=payload, headers=headers, verify=False)
            post_response.raise_for_status()
            print("MCP Instance Policy 'default' enabled.")
        else:
            print("MCP Instance Policy 'default' not enabled. Exiting.")
            exit(1)
    else:
        print("MCP Instance Policy 'default' is already enabled.")

def create_mcp_interface_policy(APIC_URL, token, policy_name):
    url = f"{APIC_URL}/api/mo/uni/infra/mcpIfP-{policy_name}.json"
    headers = {"Cookie": f"APIC-cookie={token}"}
    payload = {
        "mcpIfPol": {
            "attributes": {
                "dn": f"uni/infra/mcpIfP-{policy_name}",
                "name": policy_name,
                "adminSt": "enabled",
                "descr": "MCP Interface Policy",
                "status": "created"
            }
        }
    }
    response = requests.post(url, json=payload, headers=headers, verify=False)
    response.raise_for_status()
    print(f"MCP interface policy '{policy_name}' created/enabled.")

def get_leaf_access_port_policy_groups(APIC_URL, token):
    url = f"{APIC_URL}/api/class/infraAccPortGrp.json"
    headers = {"Cookie": f"APIC-cookie={token}"}
    response = requests.get(url, headers=headers, verify=False)
    response.raise_for_status()
    data = response.json()
    groups = [item['infraAccPortGrp']['attributes']['name'] for item in data.get('imdata', [])]
    return groups

def associate_mcp_policy_to_port_group(APIC_URL, token, policy_name, group_name):
    url = f"{APIC_URL}/api/mo/uni/infra/funcprof/accportgrp-{group_name}.json"
    headers = {"Cookie": f"APIC-cookie={token}"}
    payload = {
        "infraAccPortGrp": {
            "attributes": {
                "dn": f"uni/infra/funcprof/accportgrp-{group_name}",
                "name": group_name,
                "status": "modified"
            },
            "children": [
                {
                    "infraRsMcpIfPol": {
                        "attributes": {
                            "tnMcpIfPolName": policy_name,
                            "status": "created,modified"
                        }
                    }
                }
            ]
        }
    }
    response = requests.post(url, json=payload, headers=headers, verify=False)
    response.raise_for_status()
    print(f"MCP interface policy '{policy_name}' associated to Leaf access port policy group '{group_name}'.")

def mcp_interface_policy_exists(APIC_URL, token, policy_name):
    url = f"{APIC_URL}/api/mo/uni/infra/mcpIfP-{policy_name}.json"
    headers = {"Cookie": f"APIC-cookie={token}"}
    response = requests.get(url, headers=headers, verify=False)
    if response.status_code == 200:
        data = response.json()
        if data.get('imdata'):
            return True
    return False

def main():
    csv_path = input("Enter path to CSV file with fabric credentials: ")
    fabrics = read_fabric_credentials(csv_path)
    for fabric in fabrics:
        APIC_URL = fabric["APIC_URL"]
        USERNAME = fabric["USERNAME"]
        PASSWORD = fabric["PASSWORD"]
        print(f"\n--- Processing fabric: {APIC_URL} ---")
        try:
            token = login(APIC_URL, USERNAME, PASSWORD)
        except Exception as e:
            print(f"Login failed for {APIC_URL}: {e}")
            continue
        proceed_mcp = input("Do you want to check/enable MCP Instance Policy 'default'? (y/n): ")
        if proceed_mcp.strip().lower() != 'y':
            print("Skipping MCP Instance Policy step for this fabric.")
        else:
            ensure_mcp_instance_policy_enabled(APIC_URL, token)
        proceed_ifpol = input("Do you want to create MCP Interface Policy? (y/n): ")
        if proceed_ifpol.strip().lower() != 'y':
            print("Skipping MCP Interface Policy creation for this fabric.")
        else:
            if mcp_interface_policy_exists(APIC_URL, token, policy_name):
                print(f"MCP interface policy '{policy_name}' already exists. Skipping creation.")
            else:
                create_mcp_interface_policy(APIC_URL, token, policy_name)
            proceed_assoc = input("Do you want to associate the new MCP Interface Policy to a Leaf access port policy group? (y/n): ")
            if proceed_assoc.strip().lower() == 'y':
                groups = get_leaf_access_port_policy_groups(APIC_URL, token)
                if not groups:
                    print("No Leaf access port policy groups found in the fabric.")
                    continue
                print("Available Leaf access port policy groups:")
                for idx, name in enumerate(groups, 1):
                    print(f"{idx}. {name}")
                choices = input("Enter the numbers of the groups you want to associate with the MCP policy (comma separated): ")
                try:
                    selected_indices = [int(x.strip())-1 for x in choices.split(',')]
                    selected_groups = [groups[i] for i in selected_indices if 0 <= i < len(groups)]
                except (IndexError, ValueError):
                    print("Invalid selection. Skipping association for this fabric.")
                    continue
                if not selected_groups:
                    print("No valid groups selected. Skipping association for this fabric.")
                    continue
                for group_name in selected_groups:
                    associate_mcp_policy_to_port_group(APIC_URL, token, policy_name, group_name)

if __name__ == "__main__":
    main()