import json                                                     # Импорт модуля для работы с JSON
import os                                                       # Импорт модуля для работы с операционной системой
import sys                                                      # Импорт модуля для работы с системными функциями
from pathlib import Path                                        # Импорт класса Path для работы с путями

CONFIG_FILE = Path(__file__).parent / 'repofresh_config.json'   # Определение пути к конфигурационному файлу


def load_config():                                              # Загружает конфигурацию из JSON-файла.

    if not CONFIG_FILE.exists():                                # Проверка существования конфигурационного файла
                                                                # Создаем начальную конфигурацию с пустым списком репозиториев
        initial_config = {
            "repositories": [],
            "version": "1.0",
            "config_path": str(CONFIG_FILE)
        }
        save_config(initial_config)                             # Сохранение начальной конфигурации
        print(f""
              f"Создан новый конфигурационный файл: {CONFIG_FILE}")  # Информационное сообщение
        return initial_config                                   # Возврат начальной конфигурации

    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:     # Открытие файла для чтения
            config = json.load(f)                               # Загрузка данных из JSON
        print(f"Конфигурация загружена из: {CONFIG_FILE}")      # Сообщение об успешной загрузке
        return config                                           # Возврат загруженной конфигурации

    except (json.JSONDecodeError, KeyError) as e:               # Обработка ошибок чтения JSON
        print(f"Ошибка чтения конфигурационного файла: {e}")
        sys.exit(1)


def save_config(config):                                        # Сохраняет конфигурацию в JSON-файл.
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:     # Открытие файла для записи
            json.dump(config, f, indent=2, ensure_ascii=False)  # Запись данных в JSON с форматированием
        return True                                             # Возврат успешного статуса
    except Exception as e:                                      # Обработка любых ошибок записи
        print(f"Ошибка сохранения конфигурации: {e}")           # Сообщение об ошибке
        return False                                            # Возврат статуса ошибки


def is_valid_git_repository(path):                              # Проверяет, является ли путь валидным Git-репозиторием.
    expanded_path = os.path.expanduser(path)                    # Раскрытие символа ~ в пути

    if not os.path.exists(expanded_path):                       # Проверка существования пути
        print(f"Путь не существует: {expanded_path}")
        return False

    if not os.path.isdir(expanded_path):                        # Проверка что путь ведет к директории
        print(f"Путь не является директорией: {expanded_path}")
        return False

    git_dir = os.path.join(expanded_path, '.git')               # Формирование пути к папке .git
    if not os.path.exists(git_dir):                             # Проверка существования папки .git
        print(f"Директория не является Git-репозиторием: {expanded_path}")
        return False

    return True                                                 # Возврат true если все проверки пройдены


def get_repo_name_suggestion(path):                             # Предлагает название репозитория на основе пути.
    expanded_path = os.path.expanduser(path)                    # Раскрытие символа ~ в пути
    base_name = os.path.basename(expanded_path)                 # Получение имени папки из пути
    return base_name                                            # Возврат предложенного имени


def is_unique_repo_name(config, name):                          # Проверяет, что название репозитория уникально.
    for repo in config['repositories']:                         # Перебор всех репозиториев
        if repo['name'] == name:                                # Проверка совпадения имени
            return False                                        # Возврат false если имя уже используется
    return True                                                 # Возврат true если имя уникально


def is_unique_repo_path(config, path):                          # Проверяет, что путь репозитория уникален.
    expanded_path = os.path.abspath(os.path.expanduser(path))   # Нормализация пути
    for repo in config['repositories']:                         # Перебор всех репозиториев
        if repo['path'] == expanded_path:                       # Проверка совпадения пути
            return False                                        # Возврат false если путь уже используется
    return True                                                 # Возврат true если путь уникален


def add_repository(config):                                     # Добавляет новый репозиторий в конфигурацию.
    path = input("Введите путь к Git-репозиторию: ").strip()    # Запрос пути у пользователя

    if not path:                                                # Проверка что путь не пустой
        print("Путь не может быть пустым.")
        return

    if not is_valid_git_repository(path):                       # Проверка валидности репозитория
        return

    if not is_unique_repo_path(config, path):                   # Проверка что путь еще не добавлен
        print(f"Репозиторий с таким путем уже добавлен.")
        return

    expanded_path = os.path.abspath(os.path.expanduser(path))   # Нормализация пути

    suggested_name = get_repo_name_suggestion(path)             # Получение предложенного имени
    print(f"Предлагаемое название: '{suggested_name}'")         # Вывод предложенного имени

    name = input("Введите название репозитория (или Enter для предложенного): ").strip()  # Запрос названия

    if not name:                                                # Проверка что пользователь ввел название
        name = suggested_name                                   # Использование предложенного имени

    if not is_unique_repo_name(config, name):                   # Проверка уникальности имени
        print(f"Репозиторий с названием '{name}' уже существует.")
        return

    new_repo = {                                                # Создание словаря с данными репозитория
        "name": name,                                           # Название репозитория
        "path": expanded_path,                                  # Путь к репозиторию
    }

    config['repositories'].append(new_repo)                     # Добавление репозитория в список

    if save_config(config):                                     # Сохранение обновленной конфигурации
        print(f"Репозиторий успешно добавлен!")
        print(f"Название: {name}")
        print(f"Путь: {expanded_path}")
        print(f"Всего репозиториев: {len(config['repositories'])}")
    else:
        return


def remove_repository(config):                                  # Удаляет репозиторий из списка по названию.
    repositories = config['repositories']                       # Получение списка репозиториев из конфига

    if not repositories:                                        # Проверка что список не пустой
        print("Список репозиториев пуст. Нечего удалять.")
        return

    print("\nТекущие репозитории:")                             # Заголовок списка
    for i, repo in enumerate(repositories, 1):                  # Перебор репозиториев с нумерацией
        print(f"{i}. {repo['name']} - {repo['path']}")          # Вывод номера, названия и пути

    repo_name = input("\nВведите название репозитория для удаления: ").strip()  # Запрос названия для удаления

    if not repo_name:                                           # Проверка что название не пустое
        print("Название не может быть пустым.")
        return

    found_index = -1                                            # Инициализация переменной для найденного индекса
    for i, repo in enumerate(repositories):                     # Перебор репозиториев для поиска по имени
        if repo['name'] == repo_name:                           # Проверка совпадения названия
            found_index = i                                     # Сохранение найденного индекса
            break                                               # Выход из цикла поиска

    if found_index != -1:                                       # Проверка что репозиторий найден
        removed_repo = repositories.pop(found_index)            # Удаление репозитория из списка по индексу
        if save_config(config):                                 # Сохранение обновленной конфигурации
            print(f"Репозиторий '{removed_repo['name']}' успешно удален!")  # Сообщение об успехе
            print(f"Осталось репозиториев: {len(repositories)}")  # Вывод оставшегося количества
        else:
            print("Ошибка при сохранении конфигурации.")
    else:
        print(f"Репозиторий с названием '{repo_name}' не найден.")


def clear_all_repositories(config):                             # Очищает весь список репозиториев.
    repositories = config['repositories']                       # Получение списка репозиториев из конфига

    if not repositories:                                        # Проверка что список не пустой
        print("Список репозиториев уже пуст.")
        return

    print(f"Вы собираетесь удалить ВСЕ репозитории ({len(repositories)} шт.)!")  # Предупреждение
    confirm = input("Вы уверены? (да/нет): ").strip().lower()   # Запрос подтверждения

    if confirm == 'да':                                         # Проверка подтверждения (русская и английская y)
        config['repositories'] = []                             # Очистка списка репозиториев
        if save_config(config):                                 # Сохранение пустой конфигурации
            print("Все репозитории успешно удалены!")
        else:
            print("Ошибка при сохранении конфигурации.")
    else:
        print("Удаление отменено.")


def list_repositories(config):                                  # Выводит список всех добавленных репозиториев.
    repositories = config['repositories']                       # Получение списка репозиториев из конфига

    if not repositories:                                        # Проверка что список не пустой
        print("Список репозиториев пуст.")
        return

    print(f"Всего репозиториев: {len(repositories)}")           # Вывод количества репозиториев
    print()

    for i, repo in enumerate(repositories, 1):                  # Перебор репозиториев с нумерацией
                                                                # Проверяем, существует ли репозиторий
        if os.path.exists(repo['path']):                        # Проверка существования пути
            status = "Обновлен"
        else:
            status = "Требует обновления"

        print(f"{i:2d}. {status} {repo['name']} {repo['path']}")  # Вывод инфы о репозитории
        print()


def show_menu():                                                # Показывает главное меню программы.
    print("1. Показать список репозиториев")                    # Пункт меню 1
    print("2. Добавить репозиторий")                            # Пункт меню 2
    print("3. Удалить репозиторий (по названию)")               # Пункт меню 3
    print("4. Очистить весь список")                            # Пункт меню 4
    print("5. Выход")                                           # Пункт меню 5


def main():                                                     # Основная функция программы.
    config = load_config()                                      # Загрузка конфигурации

    while True:                                                 # Бесконечный цикл меню
        show_menu()                                             # Отображение меню

        try:
            choice = input("\nВыберите действие (1-5): ").strip()  # Запрос выбора у пользователя

            if choice == '1':
                list_repositories(config)                       # Показать список репозиториев
            elif choice == '2':
                add_repository(config)                          # Добавить репозиторий
            elif choice == '3':
                remove_repository(config)                       # Удалить репозиторий
            elif choice == '4':
                clear_all_repositories(config)                  # Очистить весь список
            elif choice == '5':
                break                                           # Выход из цикла
            else:
                print("Неверный выбор. Пожалуйста, выберите от 1 до 5.")

            input("\nНажмите Enter для продолжения...")         # Ожидание нажатия Enter

        except KeyboardInterrupt:                               # Обработка прерывания (Ctrl+C)
            print("\n\nПрограмма прервана пользователем.")      # Сообщение о прерывании
            break                                               # Выход из цикла
        except Exception as e:                                  # Обработка всех остальных ошибок
            print(f"\nПроизошла ошибка: {e}")                   # Вывод сообщения об ошибке


if __name__ == '__main__':
    main()                                                      # Запуск основной функции