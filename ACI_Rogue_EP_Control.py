###########################
# Global setting - Enabling Rogue Endpoint Control
# Flow of the code is as follows:
# 1. Reads a CSV file containing multiple ACI fabric credentials.
# 2. Logs into each fabric using the provided credentials.
# 3. Checks if Rogue Endpoint Control is enabled in Global Fabric Policies.
# 4. If not enabled, prompts the user to enable it.
# 5. Enables Rogue Endpoint Control if the user agrees.
###########################

import requests
import urllib3
import csv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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

def ensure_rogue_ep_control_enabled(APIC_URL, token):
    url = f"{APIC_URL}/api/mo/uni/infra/epCtrlP-default.json"
    headers = {"Cookie": f"APIC-cookie={token}"}
    response = requests.get(url, headers=headers, verify=False)
    response.raise_for_status()
    data = response.json()
    enabled = False
    if data.get('imdata'):
        attrs = data['imdata'][0]['epControlP']['attributes']
        if attrs.get('adminSt', '').lower() == 'enabled':
            enabled = True
    if not enabled:
        print("Rogue EP Control is not enabled.")
        choice = input("Do you want to enable Rogue EP Control? (y/n): ")
        if choice.strip().lower() == 'y':
            payload = {
                "epControlP": {
                    "attributes": {
                        "dn": "uni/infra/epCtrlP-default",
                        "adminSt": "enabled",
                        "status": "modified",
                        "holdIntvl": "1800",
                        "rogueEpDetectIntvl": "60",
                        "rogueEpDetectMult": "4"
                    }
                }
            }
            post_url = f"{APIC_URL}/api/mo/uni/infra/epCtrlP-default.json"
            post_response = requests.post(post_url, json=payload, headers=headers, verify=False)
            post_response.raise_for_status()
            print("Rogue EP Control enabled.")
        else:
            print("Rogue EP Control not enabled. Exiting.")
            exit(1)
    else:
        print("Rogue EP Control is already enabled.")

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
        ensure_rogue_ep_control_enabled(APIC_URL, token)

if __name__ == "__main__":
    main()