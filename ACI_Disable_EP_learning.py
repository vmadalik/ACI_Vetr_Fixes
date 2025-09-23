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

def ensure_disable_remote_ep_learning(APIC_URL, token):
    url = f"{APIC_URL}/api/mo/uni/infra/settings.json"
    headers = {"Cookie": f"APIC-cookie={token}"}
    response = requests.get(url, headers=headers, verify=False)
    response.raise_for_status()
    data = response.json()
    disabled = False
    if data.get('imdata'):
        attrs = data['imdata'][0]['infraSetPol']['attributes']
        if attrs.get('remoteEpLearn', '').lower() == 'disabled':
            disabled = True
    if not disabled:
        print("Remote EP Learning is not disabled.")
        choice = input("Do you want to disable Remote EP Learning? (y/n): ")
        if choice.strip().lower() == 'y':
            payload = {
                "infraSetPol": {
                    "attributes": {
                        "dn": "uni/infra/settings",
                        "unicastXrEpLearnDisable": "yes",
                        "status": "modified"
                    }
                }
            }
            post_url = f"{APIC_URL}/api/mo/uni/infra/settings.json"
            post_response = requests.post(post_url, json=payload, headers=headers, verify=False)
            post_response.raise_for_status()
            print("Remote EP Learning disabled.")
        else:
            print("Remote EP Learning not disabled. Exiting.")
            exit(1)
    else:
        print("Remote EP Learning is already disabled.")

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
        ensure_disable_remote_ep_learning(APIC_URL, token)

if __name__ == "__main__":
    main()
