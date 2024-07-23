import requests
import pandas as pd

organization = 'GAAzdoDevOpsPROD'
project = 'GIT_GA_CSD_ADMT_RePlatforming'
pat = ''
team_name_to_fetch = 'GIT_GA_CSD_ADMT_RePlatforming Team' 

# API URL to get teams
url = f'https://dev.azure.com/{organization}/_apis/projects/{project}/teams?api-version=6.0'

# Make the API request to get teams
response = requests.get(url, auth=('', pat))
teams = response.json()['value']

# Initialize list to store user details
users_list = []

# Find the specified team and get its members
for team in teams:
    if team['name'] == team_name_to_fetch:
        team_id = team['id']
        team_url = f'https://dev.azure.com/{organization}/_apis/projects/{project}/teams/{team_id}/members?api-version=6.0'

        # Initialize pagination parameters
        page = 1
        limit = 100

        while True:
            params = {"$top": limit, "$skip": (page - 1) * limit}
            team_response = requests.get(team_url, params=params, auth=('', pat))
            team_data = team_response.json()
            team_members = team_data['value']

            # Debug print to check the team members data
            print(f"Fetched {len(team_members)} members on page {page}")

            # Collect member details from the 'identity' dictionary
            for member in team_members:
                identity = member.get('identity', {})
                users_list.append({
                    'Team': team_name_to_fetch,
                    'User ID': identity.get('id', 'N/A'),
                    'User Name': identity.get('displayName', 'N/A'),
                    'Email': identity.get('uniqueName', 'N/A')
                })

            # Check if there are more members to fetch
            if len(team_members) < limit:
                break
            page += 1

# Create a DataFrame and save it to an Excel file
if users_list:
    df = pd.DataFrame(users_list)
    excelFileName = f'AzDo_Users_{team_name_to_fetch}.xlsx'
    df.to_excel(excelFileName, index=False)
    print("Excel file has been created successfully.")
else:
    print(f"No users found for team: {team_name_to_fetch}")
