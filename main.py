import os
import sys
from crypto_module import CryptoModule
from stego_module import StegoModule
from analysis_module import AnalysisModule


def embed_message():
    print("\n--- ВСТРАИВАНИЕ СООБЩЕНИЯ ---")
    
    message_file = input("Файл с сообщением (txt): ").strip()
    if not os.path.exists(message_file):
        print(f"Ошибка: файл '{message_file}' не найден!")
        return
    
    password = input("Пароль: ").strip()
    if not password:
        print("Ошибка: пароль не может быть пустым!")
        return
    
    image_path = input("Изображение-контейнер: ").strip()
    if not os.path.exists(image_path):
        print(f"Ошибка: файл '{image_path}' не найден!")
        return
    
    output_name = input("Имя для стегоизображения (без расширения): ").strip()
    if not output_name:
        output_name = "stego_output"
    
    try:
        with open(message_file, 'r', encoding='utf-8') as f:
            message = f.read()
        print(f"Прочитано сообщение длиной {len(message)} символов")
    except Exception as e:
        print(f"Ошибка чтения файла: {e}")
        return
    
    print("\n[1/3] Шифрование сообщения...")
    try:
        data_to_embed = CryptoModule.prepare_data_for_embedding(message, password)
        print(f"Подготовлено {len(data_to_embed)} байт для встраивания")
    except Exception as e:
        print(f"Ошибка шифрования: {e}")
        return
    
    print("[2/3] Встраивание данных (гибридный метод)...")
    hybrid_output = output_name + "_hybrid.png"
    success = StegoModule.embed_data_with_metadata(
        image_path, data_to_embed, password, hybrid_output
    )
    
    if not success:
        print("Не удалось встроить данные (недостаточно емкости)")
        return
    
    print("[3/3] Встраивание данных (простой LSB)...")
    simple_output = output_name + "_simple.png"
    StegoModule.simple_lsb_embed(image_path, data_to_embed, simple_output)
    
    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТ:")
    print(f"1. Гибридный метод: {hybrid_output}")
    print(f"2. Простой LSB: {simple_output}")
    print("=" * 60)

def extract_message():
    print("\n--- ИЗВЛЕЧЕНИЕ СООБЩЕНИЯ ---")
    
    stego_path = input("Стегоизображение: ").strip()
    if not os.path.exists(stego_path):
        print(f"Ошибка: файл '{stego_path}' не найден!")
        return
    
    password = input("Пароль: ").strip()
    if not password:
        print("Ошибка: пароль не может быть пустым!")
        return
    
    output_file = input("Файл для сохранения (txt): ").strip()
    if not output_file:
        output_file = "extracted_message.txt"
    
    print("\n[1/2] Извлечение данных из изображения...")
    try:
        extracted_data = StegoModule.extract_data_with_metadata(stego_path, password)
        print(f"Извлечено {len(extracted_data)} байт")
    except Exception as e:
        print(f"Ошибка извлечения: {e}")
        return
    
    print("[2/2] Расшифровка сообщения...")
    try:
        message = CryptoModule.extract_and_decrypt(extracted_data, password)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(message)
        
        print("\n" + "=" * 60)
        print("УСПЕШНО ИЗВЛЕЧЕНО!")
        print(f"Сообщение сохранено в: {output_file}")
        print("\nПРЕДПРОСМОТР:")
        print("-" * 40)
        if len(message) > 200:
            print(message[:200] + "...")
        else:
            print(message)
        print("-" * 40)
        print("=" * 60)
        
    except ValueError as e:
        print(f"Ошибка: {e}")
        print("Возможные причины:")
        print("1. Неправильный пароль")
        print("2. Повреждено стегоизображение")
        print("3. Файл не содержит скрытых данных")
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")

def compare_methods():
    print("\n--- СРАВНЕНИЕ МЕТОДОВ ---")
    
    original = input("Оригинальное изображение: ").strip()
    simple = input("Изображение с простым LSB: ").strip()
    hybrid = input("Изображение с гибридным методом: ").strip()
    
    if not all(os.path.exists(f) for f in [original, simple, hybrid]):
        print("Ошибка: один или несколько файлов не найдены!")
        return
    
    print("\nАнализ изображений...")
    results = AnalysisModule.compare_methods(original, simple, hybrid)
    
    with open("report.txt", "w", encoding="utf-8") as f:
        f.write("ОТЧЕТ О СРАВНЕНИИ МЕТОДОВ СТЕГАНОГРАФИИ\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"1. Качество (PSNR):\n")
        f.write(f"   - Простой LSB: {results['psnr_simple']:.2f} dB\n")
        f.write(f"   - Гибридный метод: {results['psnr_hybrid']:.2f} dB\n\n")
        
        f.write(f"2. Измененные пиксели:\n")
        f.write(f"   - Простой LSB: {results['changed_pixels_simple']:,}\n")
        f.write(f"   - Гибридный метод: {results['changed_pixels_hybrid']:,}\n\n")
        
        f.write("3. ВЫВОДЫ:\n")
        if results['psnr_hybrid'] > results['psnr_simple']:
            f.write("   ✓ Гибридный метод менее заметен (выше PSNR)\n")
        else:
            f.write("   ✓ Простой LSB менее заметен (выше PSNR)\n")

    
    print(f"\nОтчет сохранен в: comparison_report.txt")
    print(f"Графики сохранены в: comparison_results.png")

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    
    while True:
        print("\nМЕНЮ:")
        print("1. Зашифровать и встроить сообщение")
        print("2. Извлечь и расшифровать сообщение")
        print("3. Сравнить методы стеганографии")
        print("4. Выйти")
        
        choice = input("\nВыберите действие (1-4): ").strip()
        
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