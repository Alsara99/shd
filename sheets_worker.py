import gspread
from google.oauth2.service_account import Credentials
from platrum_worker import get_tasks
from datetime import datetime


GOOGLE_CREDENTIALS = "credentials.json"

SPREADSHEET_NAME = "Platrum Dashboard"


def get_or_create_sheet(employee):
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    credentials = Credentials.from_service_account_file(
        GOOGLE_CREDENTIALS,
        scopes=scopes
    )

    client = gspread.authorize(credentials)

    spreadsheet = client.open(SPREADSHEET_NAME)

    worksheet_name = employee

    try:
        worksheet = spreadsheet.worksheet(worksheet_name)
    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(
            title=worksheet_name,
            rows=1000,
            cols=10
        )

    return worksheet


def prepare_rows(employee):

    rows = [[
        "сколько сейчас стоит задач",
        "сколько выполнено",
        "сколько выполнено с просрочкой",
        "сколько не выполнено",
        "сколько просрочено",
    ]]

    tasks = get_tasks({
        "responsible_user_ids": [employee]
    })

    total_tasks = len(tasks)

    finished_tasks = [
        task
        for task in tasks
        if task.get("status_key") == "finished"
    ]

    unfinished_tasks = [
        task
        for task in tasks
        if task.get("status_key") != "finished"
    ]

    deadlined_finished_tasks = 0

    for task in finished_tasks:

        finish_date = task.get("finish_date")
        close_date = task.get("close_date")

        if not finish_date or not close_date:
            continue

        deadline = datetime.strptime(
            finish_date,
            "%Y-%m-%dT%H:%M:%SZ"
        )

        closed = datetime.strptime(
            close_date,
            "%Y-%m-%dT%H:%M:%SZ"
        )

        if closed > deadline:
            deadlined_finished_tasks += 1

    deadlined_tasks = 0

    for task in unfinished_tasks:

        finish_date = task.get("finish_date")

        if not finish_date:
            continue

        deadline = datetime.strptime(
            finish_date,
            "%Y-%m-%dT%H:%M:%SZ"
        )

        if deadline < datetime.now():
            deadlined_tasks += 1

    rows.append([
        total_tasks,
        len(finished_tasks),
        deadlined_finished_tasks,
        len(unfinished_tasks),
        deadlined_tasks
    ])

    return rows


def upload_staff_sheets(staff):
    for employee in staff:
        worksheet = get_or_create_sheet(staff[employee].get("name"))
        worksheet.clear()

        rows = prepare_rows(employee)

        worksheet.update(
            range_name="A1",
            values=rows
        )

        worksheet.format(
            "A1:E1000",
            {
                "wrapStrategy": "WRAP"
            }
        )

        print(f"Google Sheets {staff[employee].get("name")} обновлена.")
