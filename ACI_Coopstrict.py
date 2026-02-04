"""ACI COOP Strict Mode helper.

Reads fabric credentials from CSV, logs in to each APIC, checks COOP strict
policy, and optionally enables it when disabled.
"""

######################################
# ACI COOP Strict Mode Script
# Flow of the code is as follows:
# 1. Reads a CSV file containing multiple ACI fabric credentials.
# 2. Logs into each fabric using the provided credentials.
# 3. Checks if COOP Strict Mode is enabled in Global Fabric Policies.
# 4. If not enabled, prompts the user to enable it.
# 5. Enables COOP Strict Mode if the user agrees.
########################################
import requests
import urllib3
import csv
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def read_fabric_credentials(csv_path):
    """Load APIC URL/username/password entries from a CSV file."""
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
    """Authenticate to APIC and return the session token."""
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

def ensure_coop_strict_enabled(APIC_URL, token):
    """Check COOP strict policy and optionally enable it."""
    url = f"{APIC_URL}/api/mo/uni/fabric/pol-default.json"
    headers = {"Cookie": f"APIC-cookie={token}"}
    response = requests.get(url, headers=headers, verify=False)
    response.raise_for_status()
    data = response.json()
    enabled = False
    if data.get('imdata'):
        attrs = data['imdata'][0]['coopPol']['attributes']
        if attrs.get('type', '').lower() == 'strict':
            enabled = True
    if not enabled:
        print("COOP Strict Mode is not enabled.")
        choice = input("Do you want to enable COOP Strict Mode? (y/n): ")
        if choice.strip().lower() == 'y':
            payload = {
                "coopPol": {
                    "attributes": {
                        "dn": "uni/fabric/pol-default",
                        "type": "strict",
                        "status": "modified"
                    }
                }
            }
            post_url = f"{APIC_URL}/api/mo/uni/fabric/pol-default.json"
            post_response = requests.post(post_url, json=payload, headers=headers, verify=False)
            post_response.raise_for_status()
            print("COOP Strict Mode enabled.")
        else:
            print("COOP Strict Mode not enabled. Skipping this fabric.")
    else:
        print("COOP Strict Mode is already enabled.")

def main():
    """Entry point for prompting and processing fabrics."""
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
        print(f"\n--- Processing fabric: {APIC_URL} ---")
        try:
            token = login(APIC_URL, USERNAME, PASSWORD)
        except Exception as e:
            print(f"Login failed for {APIC_URL}: {e}")
            continue
        ensure_coop_strict_enabled(APIC_URL, token)

if __name__ == "__main__":
    main()
