from dns_cache import DNSCache


def print_record(record):
    if record is None:
        print("Запись не найдена или устарела.")
        return

    print("DNS-запись:")
    print(f"  Домен: {record.domain}")
    print(f"  Тип: {record.record_type}")
    print(f"  Значение: {record.value}")
    print(f"  TTL: {record.ttl}")
    print(f"  Время добавления: {record.added_at}")
    print(f"  Источник: {record.source}")


def read_int(prompt):
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Введите целое число.")


def menu():
    print()
    print("=== DNS Cache ===")
    print("1. Добавить запись")
    print("2. Удалить запись")
    print("3. Обновить TTL")
    print("4. Найти запись по домену и типу")
    print("5. Удалить устаревшие записи")
    print("6. Вывести количество записей каждого типа")
    print("7. Сохранить в файл")
    print("8. Загрузить из файла")
    print("9. Показать общее количество записей")
    print("0. Выход")


def main():
    cache = DNSCache(initial_capacity=1024)

    while True:
        menu()
        choice = input("Выберите действие: ").strip()

        try:
            if choice == "1":
                domain = input("Домен: ")
                record_type = input("Тип записи: ")
                value = input("IP-адрес или значение: ")
                ttl = read_int("TTL в секундах: ")
                source = input("Источник: ")

                is_new = cache.add_record(domain, record_type, value, ttl, source)
                if is_new:
                    print("Запись добавлена.")
                else:
                    print("Запись с таким доменом и типом уже была, она заменена.")

            elif choice == "2":
                domain = input("Домен: ")
                record_type = input("Тип записи: ")
                if cache.delete_record(domain, record_type):
                    print("Запись удалена.")
                else:
                    print("Запись не найдена.")

            elif choice == "3":
                domain = input("Домен: ")
                record_type = input("Тип записи: ")
                ttl = read_int("Новый TTL: ")
                if cache.update_ttl(domain, record_type, ttl):
                    print("TTL обновлен.")
                else:
                    print("Запись не найдена.")

            elif choice == "4":
                domain = input("Домен: ")
                record_type = input("Тип записи: ")
                print_record(cache.find_record(domain, record_type))

            elif choice == "5":
                removed = cache.remove_expired()
                print(f"Удалено устаревших записей: {removed}")

            elif choice == "6":
                counts = cache.count_by_type()
                if not counts:
                    print("Записей нет.")
                else:
                    print("Количество записей каждого типа:")
                    for record_type, count in counts:
                        print(f"  {record_type}: {count}")

            elif choice == "7":
                filename = input("Имя файла: ")
                cache.save_to_file(filename)
                print("Данные сохранены.")

            elif choice == "8":
                filename = input("Имя файла: ")
                cache.load_from_file(filename)
                print("Данные загружены.")

            elif choice == "9":
                print(f"Всего записей: {cache.size}")

            elif choice == "0":
                print("Выход.")
                break

            else:
                print("Неизвестная команда.")

        except Exception as error:
            print(f"Ошибка: {error}")


if __name__ == "__main__":
    main()
