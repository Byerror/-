import os
import subprocess
import requests
import zipfile
import sys

# Установите URL-адреса для загрузки файлов
PYTHON_INSTALLER_URL = "https://www.python.org/ftp/python/3.11.6/python-3.11.6-amd64.exe"
INSTALLALL_SCRIPT_URL = "https://files.azimoff.systems/installall.py"
UPDATE_ZIP_URL = "https://files.azimoff.systems/updates/update.zip"

# Минимальная версия Python, которая требуется
MIN_PYTHON_VERSION = (3, 11, 6)

# Скачивание файла
def download_file(url, local_filename):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_filename

# Проверка наличия установленного Python и его версии
def check_python_version():
    try:
        output = subprocess.check_output(["python", "--version"], stderr=subprocess.STDOUT)
        version = output.decode().strip().split()[1]
        major, minor, micro = map(int, version.split('.'))
        if (major, minor, micro) >= MIN_PYTHON_VERSION:
            print(f"Установлена подходящая версия Python: {version}")
            return True
        else:
            print(f"Установлена неподходящая версия Python: {version}")
            return False
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Python не установлен.")
        return False

# Установка Python
def install_python():
    python_installer = download_file(PYTHON_INSTALLER_URL, "python-3.11.6-amd64.exe")
    subprocess.run([python_installer, "/quiet", "InstallAllUsers=1", "PrependPath=1"])
    os.remove(python_installer)

# Запуск файла installall.py
def run_installall_script():
    installall_script = download_file(INSTALLALL_SCRIPT_URL, "installall.py")
    subprocess.run(["python", installall_script])
    os.remove(installall_script)

# Распаковка архива
def download_and_extract_update():
    update_zip = download_file(UPDATE_ZIP_URL, "update.zip")
    with zipfile.ZipFile(update_zip, 'r') as zip_ref:
        zip_ref.extractall("ВАШЕ КАЗИНО")
    os.remove(update_zip)

# Обновление config.py
def update_config():
    config_path = os.path.join("ВАШЕ КАЗИНО", "config.py")
    config_data = {
        "CHANNEL_ID": input("Введите айди канала в Telegram со ставками: "),
        "INVOICE_LINK": input("Введите ссылку на счет (получается в CryptoBot): "),
        "RULES_LINK": input("Введите ссылку на правила/пользовательское соглашение: "),
        "NEWS_LINK": input("Введите ссылку на новости: "),
        "SUPPORT_LINK": input("Введите ссылку на техподдержку: "),
        "FAQ_LINK": input("Введите ссылку на FAQ: "),
        "CRYPTO_PAY_TOKEN": input("Введите токен от CryptoPay (получается в CryptoBot): "),
        "BOT_TOKEN": input("Введите токен бота Telegram: "),
        "SCAM_SUM": input("Введите скам сумму: "),
        "SCAM_SUM_WHEEL": 10,
        "SCAM_WHEEL": 0,
        "ADMIN_ID": input("Введите айди TG первого администратора: "),
        "ADMIN_SD": input("Введите айди TG второго администратора: "),
        "NEWS_ID": input("Введите айди телеграмм канала новостей: "),
        "VIPLAT_ID": input("Введите айди телеграмм канала с выплатами: "),
        "WIN_IMAGE": input("Вставьте ссылку с imgur на изображение победы: "),
        "LOSE_IMG":  input("Вставьте ссылку с imgur на изображение проигрыша: "),
        "CHAT_LINK": input("Введите ссылку на чат: "),
        "CHAT_MESSAGE_INTERVAL": input("Введите интервал приглашения в чат (в секундах): "),
        "OFFLINE_DOLLAR": 92,
        "ERROR_CHAT_ID": input("Введите айди чата с ошибками (бот должен быть в нем): "),
        "MAX_BET": input("Введите сумму максимальной ставки: ")
    }

    with open(config_path, 'w') as config_file:
        for key, value in config_data.items():
            if isinstance(value, str):
                config_file.write(f'{key} = "{value}"\n')
            else:
                config_file.write(f'{key} = {value}\n')

def main():
    if not check_python_version():
        response = input("Хотите установить подходящую версию Python? (y/n): ")
        if response.lower() == 'y':
            install_python()
            print("Python установлен.")
        else:
            print("Установка прервана пользователем.")
            sys.exit(1)
    else:
        print("Подходящая версия Python уже установлена.")

    run_installall_script()
    print("Скрипт installall.py выполнен.")
    
    download_and_extract_update()
    print("Обновление скачано и распаковано.")
    
    update_config()
    print("Файл config.py обновлен.")

    print("\n\n Установка завершена. \n\n")

if __name__ == "__main__":
    main()
