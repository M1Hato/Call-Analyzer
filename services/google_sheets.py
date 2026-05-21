import gspread
from services.google_drive import get_user_credentials
from config import settings


def get_sheets_client():
    creds = get_user_credentials()
    return gspread.authorize(creds)


def append_call_to_sheet(file_name: str, analysis_data):
    client = get_sheets_client()
    spreadsheet = client.open_by_key(settings.TABLE)
    sheet = spreadsheet.get_worksheet(0)

    calculated_score = analysis_data.total_score

    row_to_add = [
        file_name,  # A: Дата (Назва файлу)
        analysis_data.call_purpose,  # B: Тип звернення
        "",  # C: Номер телефону
        "",  # D: Філія
        "",  # E: Менеджер
        analysis_data.intro_done,  # F: Скрипт (Початок)
        analysis_data.car_body_asked,  # G: Дізнався кузов
        analysis_data.car_year_asked,  # H: Дізнався рік
        analysis_data.car_mileage_asked,  # I: Дізнався пробіг
        analysis_data.diagnostic_offered,  # J: Пропозиція діагностики
        analysis_data.previous_works_asked,  # K: Які роботи робилися раніше
        analysis_data.booking_date,  # L: Запис на сервіс, Дата (заповниться, якщо є запис)
        analysis_data.goodbye_done,  # M: Завершення розмови
        analysis_data.selected_work,  # N: Яка робота з топ 100
        analysis_data.followed_top100_instructions,  # O: Чи дотримувався інструкцій з топ 100 (1/0)
        analysis_data.failed_recommendations,  # P: Яких рекомендацій менеджер не дотримувався
        analysis_data.call_result,  # Q: Результат
        calculated_score,  # R: Оцінка (тепер тут сума одиничок!)
        "",  # S: Запчастини
        analysis_data.ai_comment,  # T: Коментар
        1 if analysis_data.is_ok else 0  # U: Підрахунок балів (загальний статус успішності 1/0)
    ]

    append_result = sheet.append_row(row_to_add)

    try:
        updated_range = append_result.get('updates', {}).get('updatedRange', '')
        inserted_row_index = int(updated_range.split('!')[-1].split(':')[0][1:])
    except Exception:
        inserted_row_index = len(sheet.get_all_values())

    if not analysis_data.is_ok or calculated_score < 4:
        red_background = {"backgroundColor": {"red": 1.0, "green": 0.85, "blue": 0.85}}
        sheet.format(f"A{inserted_row_index}:U{inserted_row_index}", red_background)

    print(f"[Гугл Таблиця] Запис додано! Рядок: {inserted_row_index}. Нараховано балів (Оцінка): {calculated_score}")


def get_processed_files() -> set:
    client = get_sheets_client()
    spreadsheet = client.open_by_key(settings.TABLE)
    sheet = spreadsheet.get_worksheet(0)

    try:
        existing_files = set(sheet.col_values(1))
        return existing_files
    except Exception as e:
        print(f"[Увага] Не вдалося отримати список оброблених файлів: {e}")
        return set()