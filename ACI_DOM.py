##################
# Fabric Policy - Enabling DOM
# Flow of the code is as follows:
# 1. Login to APIC and get a token.
# 2. List all policy group names in the fabric and prompt user to choose one or more.
# 3. Create a fabric node control policy to enable DOM if it doesn't exist.
# 4. Associate the created policy to the selected policy groups.
###################

import requests
import urllib3
import csv
import os

# Disable warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

policy_name = "testingDOM_vishwa"
leaf_ID = 103  # Example leaf switch ID

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
    auth_payload = {
        "aaaUser": {
            "attributes": {
                "name": USERNAME,
                "pwd": PASSWORD
            }
        }
    }
    response = requests.post(url, json=auth_payload, verify=False)
    response.raise_for_status()
    token = response.json()['imdata'][0]['aaaLogin']['attributes']['token']
    return token


# Create fabric node control policy to enable DOM
def create_fabric_node_control_policy(APIC_URL, token, policy_name):
    url = f"{APIC_URL}/api/mo/uni/fabric/nodecontrol-{policy_name}.json"
    headers = {"Cookie": f"APIC-cookie={token}"}
    payload = {
        "fabricNodeControl": {
            "attributes": {
                "dn": f"uni/fabric/nodecontrol-{policy_name}",
                "name": policy_name,
                "control": "1",  # Enable DOM
                "rn": f"nodecontrol-{policy_name}",
                "status": "created"
            }
        }
    }
    response = requests.post(url, json=payload, headers=headers, verify=False)
    response.raise_for_status()
    print(f"Fabric node control policy '{policy_name}' created/enabled.")


# Check if a fabric node control policy exists
def check_policy_exists(APIC_URL, token, policy_name):
    url = f"{APIC_URL}/api/mo/uni/fabric/nodecontrol-{policy_name}.json"
    headers = {"Cookie": f"APIC-cookie={token}"}
    response = requests.get(url, headers=headers, verify=False)
    if response.status_code == 200:
        data = response.json()
        if data.get('imdata'):
            return True
    return False


# Associate fabric node control policy to a policy group
def associate_policy_to_group(APIC_URL, token, policy_name, group_name):
    url = f"{APIC_URL}/api/mo/uni/fabric/funcprof/lenodepgrp-{group_name}.json"
    headers = {"Cookie": f"APIC-cookie={token}"}
    payload = {
        "fabricLeNodePGrp": {
            "attributes": {
                "dn": f"uni/fabric/funcprof/lenodepgrp-{group_name}",
                "name": group_name,
                "rn": f"lenodepgrp-{group_name}",
                "status": "created,modified"
            },
            "children": [
                {
                    "fabricRsMonInstFabricPol": {
                        "attributes": {
                            "tnMonFabricPolName": "default",
                            "status": "created,modified"
                        }
                    }
                },
                {
                    "fabricRsNodeCtrl": {
                        "attributes": {
                            "tnFabricNodeControlName": policy_name,
                            "status": "created,modified"
                        }
                    }
                }
            ]
        }
    }
    response = requests.post(url, json=payload, headers=headers, verify=False)
    response.raise_for_status()
    print(f"Policy '{policy_name}' associated to policy group '{group_name}'.")


# List all policy group names in the fabric and prompt user to choose one
def get_all_group_names(APIC_URL, token):
    url = f"{APIC_URL}/api/class/fabricLeNodePGrp.json"
    headers = {"Cookie": f"APIC-cookie={token}"}
    response = requests.get(url, headers=headers, verify=False)
    response.raise_for_status()
    data = response.json()
    groups = [item['fabricLeNodePGrp']['attributes']['name'] for item in data.get('imdata', [])]
    return groups


def main():
    # Default to creds.csv in the same directory
    default_csv = os.path.join(os.path.dirname(__file__), 'creds.csv')
    csv_path = input(f"Enter path to CSV file with fabric credentials (default: {default_csv}): ").strip()
    if not csv_path:
        csv_path = default_csv
    
    try:
        fabrics = read_fabric_credentials(csv_path)
    except FileNotFoundError:
        print(f"Error: File '{csv_path}' not found.")
        return
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return
    
    for fabric in fabrics:
        APIC_URL = fabric["APIC_URL"]
        USERNAME = fabric["USERNAME"]
        PASSWORD = fabric["PASSWORD"]
        print(f"\n{'='*60}")
        print(f"Processing fabric: {APIC_URL}")
        print(f"{'='*60}")
        try:
            token = login(APIC_URL, USERNAME, PASSWORD)
            print("✓ Login successful")
        except Exception as e:
            print(f"✗ Login failed for {APIC_URL}: {e}")
            continue
        
        groups = get_all_group_names(APIC_URL, token)
        if not groups:
            print("✗ No policy groups found in the fabric.")
            continue
        
        print("\nAvailable policy groups:")
        for idx, name in enumerate(groups, 1):
            print(f"  {idx}. {name}")
        
        choices = input("\nEnter the numbers of the groups you want to use (comma separated): ").strip()
        try:
            selected_indices = [int(x.strip())-1 for x in choices.split(',')]
            selected_groups = [groups[i] for i in selected_indices if 0 <= i < len(groups)]
        except (IndexError, ValueError):
            print("✗ Invalid selection. Skipping this fabric.")
            continue
        
        if not selected_groups:
            print("✗ No valid groups selected. Skipping this fabric.")
            continue
        
        print(f"\n✓ Selected groups: {', '.join(selected_groups)}")
        
        # Check and create policy
        if not check_policy_exists(APIC_URL, token, policy_name):
            print(f"\nCreating fabric node control policy '{policy_name}'...")
            create_fabric_node_control_policy(APIC_URL, token, policy_name)
        else:
            print(f"\n✓ Policy '{policy_name}' already exists. Skipping creation.")
        
        # Ask to associate
        proceed = input("\nDo you want to associate the policy to the selected groups? (y/n): ").strip().lower()
        if proceed != 'y':
            print("Skipping policy-to-group association for this fabric.")
            continue
        
        print("\nAssociating policy to groups...")
        for group_name in selected_groups:
            try:
                associate_policy_to_group(APIC_URL, token, policy_name, group_name)
            except Exception as e:
                print(f"✗ Error associating to '{group_name}': {e}")
        
        print(f"\n✓ Completed processing for {APIC_URL}")

if __name__ == "__main__":
    main()