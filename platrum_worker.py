import requests


API_KEY = "bf9b5e66-73cb-4694-bdba-d80642bb863f"
HOST = "ad7ca7e"

PLATRUM_URL = f"https://{HOST}.platrum.ru"

headers = {
    "Content-Type": "application/json",
    "Api-key": API_KEY
}


def get_staff():
    response = requests.post(
        f"{PLATRUM_URL}/company/api/staff/list",
        headers=headers,
        json={}
    )

    result = response.json()

    if result.get("status") != "success":
        raise Exception(
            f"Ошибка Platrum API: {result}"
        )

    staff = result.get("data", [])
    print(f"Количество сотрудников из списка: {len(staff)}")

    return staff


def get_tasks(data):
    response = requests.post(
        f"{PLATRUM_URL}/tasks/api/task/list",
        headers=headers,
        json=data
    )

    result = response.json()

    if result.get("status") != "success":
        raise Exception(
            f"Ошибка Platrum API: {result}"
        )

    tasks = result.get("data", [])
    print(f"Получено задач из Platrum: {len(tasks)}")

    return tasks


def get_dashboard_data():
    response = requests.post(
        f"{PLATRUM_URL}/dashboard/get-data",
        headers=headers,
        json={"dashboard_id":4}
    )

    result = response.json()

    if result.get("status") != "success":
        raise Exception(
            f"Ошибка Platrum API: {result}"
        )

    return result.get("data")


def update_dashboards(staff):
    dashboard_data = get_dashboard_data()
    dashboard_names = []
    for dashboard in dashboard_data:
        dashboard_names.append(dashboard.get("name"))
    staff_names = []

    for employee in staff:
        name = staff[employee].get("name")
        response = requests.post(
            f"{PLATRUM_URL}/dashboard/widget/iframe/save",
            headers=headers,
            json={
                "dashboard_id": 4,
                "name": name,
                "size_height": 4,
                "size_width": 6
                }
        )
        staff_names.append(name)

        if response.json().get("status") != "success":
            raise Exception(
                f"Ошибка Platrum API: {response.json()}"
            )

    for name in dashboard_names:
        if name not in staff_names:
            for dashboard_to_delete in dashboard_data:
                if dashboard_to_delete.get("name") == name:
                    response = requests.post(
                        f"{PLATRUM_URL}/dashboard/widget/iframe/delete",
                        headers=headers,
                        json={"id": dashboard_to_delete.get("id")}
                    )
                    staff_names.append(name)

                    if response.json().get("status") != "success":
                        raise Exception(
                            f"Ошибка Platrum API: {response.json()}"
                        )
