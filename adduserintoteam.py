from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication

ORGANIZATION_URL = 'https://dev.azure.com/'
PERSONAL_ACCESS_TOKEN = ''

def add_users_to_azure_devops(org_url, pat, emails):
    try:
        connection = Connection(base_url=org_url, creds=BasicAuthentication('', pat))
        client = connection.clients.get_member_entitlement_management_client()
        successes, failures = [], []

        for email in emails:
            try:
                entitlement = {"accessLevel": {"accountLicenseType": "express"},
                               "user": {"principalName": email, "subjectKind": "user"}}
                result = client.add_user_entitlement(entitlement)
                (successes if result.is_success else failures).append(email)
                print(f"{'Successfully added' if result.is_success else 'Failed to add'}: {email}")
            except Exception as ex:
                failures.append(email)
                print(f"Error adding {email}: {str(ex)}")

        print(f"\nSummary:\nSuccessfully added: {len(successes)}\nFailed: {len(failures)}")
        if successes: print("\nSuccesses:\n" + "\n".join(f"- {e}" for e in successes))
        if failures: print("\nFailures:\n" + "\n".join(f"- {e}" for e in failures))
    except Exception as ex:
        print(f"Error: {str(ex)}")

def add_user_to_group(emails, group_name):
    try:
        connection = Connection(base_url=ORGANIZATION_URL, creds=BasicAuthentication('', PERSONAL_ACCESS_TOKEN))
        graph_client = connection.clients.get_graph_client()
        groups = graph_client.list_groups()
        group_id = next((g.descriptor for g in groups.graph_groups if g.display_name == group_name), None)

        if not group_id: return False

        successes = 0
        for email in emails:
            users = graph_client.list_users()
            member_id = next((u.descriptor for u in users.graph_users if u.mail_address.lower() == email.lower()), None)
            if member_id:
                try:
                    graph_client.add_membership(member_id, group_id)
                    print(f"Added {email} to {group_name}")
                    successes += 1
                except Exception as e:
                    print(f"Failed to add {email}: {str(e)}")
            else:
                print(f"Skipping {email} - not found")

        print(f"\nSummary: Added {successes}/{len(emails)} users")
        return True
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    emails = [""]
    group_name = ""
    add_users_to_azure_devops(ORGANIZATION_URL, PERSONAL_ACCESS_TOKEN, emails)
    add_user_to_group(emails, group_name)
