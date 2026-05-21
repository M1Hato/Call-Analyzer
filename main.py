import os
import time

from services.google_drive import list_audio_files_in_source, download_file, save_transcription_to_drive
from services.gemini_service import analyze_audio_with_gemini
from services.google_sheets import append_call_to_sheet, get_processed_files


def run_pipeline():
    print("=== ЗАПУСК АНАЛІЗУ ДЗВІНКІВ ===")

    audio_files = list_audio_files_in_source()
    if not audio_files:
        print("Нових аудіофайлів для обробки не знайдено.")
        return

    print(f"Знайдено файлів у папці: {len(audio_files)}")

    processed_files = get_processed_files()
    print(f"З них вже оброблено раніше: {len(processed_files)}")

    temp_dir = "temp_audio"
    os.makedirs(temp_dir, exist_ok=True)

    for file_info in audio_files:
        file_id = file_info['id']
        file_name = file_info['name']

        if file_name in processed_files:
            print(f"[Пропуск] Файл {file_name} вже є в таблиці. Йдемо далі...")
            continue

        print(f"\n--- Обробка нового файлу: {file_name} ---")

        safe_local_name = file_name.replace('"', '').replace("'", "")
        local_file_path = os.path.join(temp_dir, safe_local_name)

        try:
            download_file(file_id, local_file_path)
            analysis_result = analyze_audio_with_gemini(local_file_path)
            save_transcription_to_drive(file_name, analysis_result.transcription)
            append_call_to_sheet(file_name, analysis_result)

            print(f"[Успіх] Файл {file_name} повністю опрацьовано!")

        except Exception as e:
            print(f"[Помилка] Не вдалося опрацювати файл {file_name}. Деталі: {e}")

        finally:
            if os.path.exists(local_file_path):
                os.remove(local_file_path)

            print("Пауза 10 секунд перед наступним файлом")
            time.sleep(10)

    try:
        os.rmdir(temp_dir)
    except OSError:
        pass

    print("\n=== ОБРОБКУ ВСІХ ФАЙЛІВ ЗАВЕРШЕНО ===")


if __name__ == "__main__":
    run_pipeline()