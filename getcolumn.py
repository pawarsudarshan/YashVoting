from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
import pandas as pd
from datetime import datetime, timedelta

# Azure DevOps connection details
organization_url = "https://dev.azure.com/"
personal_access_token = ""
project_name = "sample project"
team_name = "sample project Team"

# Establish connection to Azure DevOps
credentials = BasicAuthentication('', personal_access_token)
connection = Connection(base_url=organization_url, creds=credentials)
wit_client = connection.clients.get_work_item_tracking_client()
board_client = connection.clients.get_boards_client()


# Function to get Kanban board columns dynamically
def get_kanban_columns():
    # Get the team context
    team_context = {"project": project_name, "team": team_name}

    # Get the Kanban board (assuming the default board is named "Stories" or "Tasks")
    # You may need to adjust the board name or fetch all boards and select the right one
    boards = board_client.get_boards(team_context)
    kanban_board = next((b for b in boards if b.name in ["Stories", "Tasks"]),
                        boards[0])  # Default to first board if not found

    # Get column definitions
    columns = board_client.get_board_columns(team_context, kanban_board.id)
    column_names = [col.name for col in columns if col.name]  # Filter out any empty names
    return column_names


# Function to get all work items for the team
def get_work_items():
    query = f"""
    SELECT [System.Id], [System.Title]
    FROM WorkItems
    WHERE [System.TeamProject] = '{project_name}'
    AND [System.AreaPath] UNDER '{project_name}\\{team_name}'
    """
    wiql = {"query": query}
    query_result = wit_client.query_by_wiql(wiql).work_items
    return [wit.id for wit in query_result]


# Function to calculate time spent in each column
def calculate_time_in_columns(work_item_id, custom_columns):
    revisions = wit_client.get_work_item(work_item_id, expand="All").revisions
    column_times = {col: timedelta(0) for col in custom_columns}
    column_entries = {col: False for col in custom_columns}  # Track if work item entered the column
    previous_time = None
    previous_column = None

    for rev in revisions:
        current_time = rev.fields.get("System.ChangedDate")
        current_column = rev.fields.get("System.BoardColumn")

        if current_column in custom_columns:
            column_entries[current_column] = True

        if previous_time and previous_column in custom_columns:
            time_diff = current_time - previous_time
            column_times[previous_column] += time_diff

        previous_time = current_time
        previous_column = current_column

    # If still in a column, calculate time until now
    if previous_column in custom_columns:
        time_diff = datetime.utcnow() - previous_time
        column_times[previous_column] += time_diff

    # Convert to days and handle "DNE"
    result = {}
    for col in custom_columns:
        if column_entries[col]:
            result[col] = round(column_times[col].total_seconds() / (24 * 3600), 2)  # Days with 2 decimal places
        else:
            result[col] = "DNE"

    return result


# Main logic
custom_columns = get_kanban_columns()  # Dynamically fetch column names
print(f"Detected columns: {custom_columns}")

work_item_ids = get_work_items()
data = []

for wid in work_item_ids:
    work_item = wit_client.get_work_item(wid)
    title = work_item.fields["System.Title"]
    time_in_columns = calculate_time_in_columns(wid, custom_columns)

    row = {
        "Work Item ID": wid,
        "Work Item Title": title,
    }
    row.update(time_in_columns)
    data.append(row)

# Create a DataFrame and save to Excel
df = pd.DataFrame(data, columns=["Work Item ID", "Work Item Title"] + custom_columns)
df.to_excel("kanban_time_report.xlsx", index=False)

print("Report generated successfully as 'kanban_time_report.xlsx'")

