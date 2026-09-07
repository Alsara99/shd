import requests
from platrum_worker import get_tasks, get_staff, update_dashboards
from sheets_worker import upload_staff_sheets


def main():
    try:
        staff = get_staff()
        update_dashboards(staff)
        print("Готово!")
    except requests.exceptions.RequestException as error:
        print(
            "Ошибка при обращении к Platrum API:"
        )
        print(error)
    except Exception as error:
        print("Произошла ошибка:")
        print(error)


if __name__ == "__main__":
    main()
