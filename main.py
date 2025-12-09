import os
import sys
from crypto_module import CryptoModule
from stego_module import StegoModule
from analysis_module import AnalysisModule


def embed_message():
    print("\n--- ВСТРАИВАНИЕ СООБЩЕНИЯ ---")
    
    print("Файл с сообщением (txt):")
    message_file = input("> ").strip()
    if not os.path.exists(message_file):
        print(f"Ошибка: файл '{message_file}' не найден!")
        return
    
    print("Введите пароль:")
    password = input("> ").strip()
    if not password:
        print("Ошибка: пароль не может быть пустым!")
        return
    
    print("Подопытная фотокарточка:")
    image_path = input("> ").strip()
    if not os.path.exists(image_path):
        print(f"Ошибка: файл '{image_path}' не найден!")
        return
    
    print("Имя для стегоизображения (без расширения):")
    output_name = input("> ").strip()
    if not output_name:
        output_name = "stego_output"
    
    try:
        with open(message_file, 'r', encoding='utf-8') as f:
            message = f.read()
    except Exception as e:
        print(f"Ошибка чтения файла: {e}")
        return
    
    print("\nШифрование сообщения...")
    try:
        data_to_embed = CryptoModule.prepare_data_for_embedding(message, password)
    except Exception as e:
        print(f"Ошибка шифрования: {e}")
        return
    
    hybrid_output = "result/imgs/" + output_name + ".png"
    success = StegoModule.embed_data_with_metadata(
        image_path, data_to_embed, password, hybrid_output
    )
    
    if not success:
        print("Не удалось встроить данные (недостаточно емкости)")
        return
    
    simple_output = "result/imgs/" + output_name + "_simpleLSB.png"
    StegoModule.simple_lsb_embed(image_path, data_to_embed, simple_output)
    
    print("\n" + "=" * 60)
    print(f"Гибридный метод: {hybrid_output}")
    print(f"Простой LSB: {simple_output}")
    print("=" * 60)

def extract_message():
    print("\n--- ИЗВЛЕЧЕНИЕ СООБЩЕНИЯ ---")
    
    print("Стегоизображение:")
    stego_path = input("> ").strip()
    if not os.path.exists(stego_path):
        print(f"Ошибка: файл '{stego_path}' не найден!")
        return
    
    print("Введите пароль:")
    password = input("> ").strip()
    if not password:
        print("Ошибка: пароль не может быть пустым!")
        return
    
    print("Файл для сохранения (просто тыкни Enter и будет дефолтный txt.txt):")
    output_file = input("> ").strip()
    if not output_file:
        output_file = "txt.txt"
    output_file = "result/messages/" + output_file
    
    try:
        extracted_data = StegoModule.extract_data_with_metadata(stego_path, password)
    except Exception as e:
        print(f"Ошибка извлечения: {e}")
        return
    
    try:
        message = CryptoModule.extract_and_decrypt(extracted_data, password)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(message)
        
        print("\nЗашифрованный текст:")
        print("-" * 40)
        if len(message) > 200:
            print(message[:200] + "...")
        else:
            print(message)
        print("-" * 40)
        print(f"Сообщение сохранено в: {output_file}")
        

    except ValueError as e:
        print(f"Ошибка извлечения: {e}")
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")

def compare_methods():
    print("\n--- СРАВНЕНИЕ МЕТОДОВ ---")
    
    print("Оригинальное изображение:")
    original = input("> ").strip()
    print("Изображение с простым LSB:")
    simple = input("> ").strip()
    print("Изображение с гибридным методом:")
    hybrid = input("> ").strip()
    
    if not all(os.path.exists(f) for f in [original, simple, hybrid]):
        print("Ошибка: один или несколько файлов не найдены!")
        return
    
    print("\nАнализ изображений...")
    results = AnalysisModule.compare_methods(original, simple, hybrid)


def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    
    os.makedirs("result/imgs", exist_ok=True)
    os.makedirs("result/messages", exist_ok=True)

    while True:
        print("\nМЕНЮ:")
        print("1. Зашифровать и встроить сообщение")
        print("2. Извлечь и расшифровать сообщение")
        print("3. Сравнить методы стеганографии")
        print("4. Выйти")
        
        choice = input("\n> ").strip()
        
        if choice == "1":
            embed_message()
            input("\nНажмите Enter для продолжения...")
            os.system('cls' if os.name == 'nt' else 'clear')
            
        elif choice == "2":
            extract_message()
            input("\nНажмите Enter для продолжения...")
            os.system('cls' if os.name == 'nt' else 'clear')
            
        elif choice == "3":
            compare_methods()
            input("\nНажмите Enter для продолжения...")
            os.system('cls' if os.name == 'nt' else 'clear')
            
        elif choice == "4":
            print("\nВыход из программы...")
            sys.exit(0)
            
        else:
            print("Чел...")

try:
    main()
except KeyboardInterrupt:
    print("\n\nПрограмма прервана пользователем")
    sys.exit(0)