import random
import numpy as np
from PIL import Image
import hashlib
import struct

class StegoModule:
    @staticmethod
    def calculate_capacity(image_array: np.ndarray) -> int:
        return image_array.size
    
    @staticmethod
    def generate_positions(password: str, image_size: tuple, total_bits: int, 
                          start_index: int = 0, seed_offset: int = 0):
        seed_input = password + str(seed_offset)
        seed = int(hashlib.sha256(seed_input.encode()).hexdigest(), 16) % (2**32)
        rng = random.Random(seed)
        
        height, width = image_size[:2]
        total_pixels = height * width * 3
        
        indices = rng.sample(range(total_pixels), total_bits)
        
        positions = []
        for idx in indices:
            pixel_idx = idx // 3
            channel = idx % 3
            y = pixel_idx // width
            x = pixel_idx % width
            positions.append((y, x, channel))
        
        return positions
    
    @staticmethod
    def embed_data_with_metadata(image_path: str, data: bytes, password: str, 
                                output_path: str) -> bool:
        img = Image.open(image_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        img_array = np.array(img)
        
        data_bits_needed = len(data) * 8
        capacity = StegoModule.calculate_capacity(img_array)
        
        
        if data_bits_needed > capacity:
            print(f"[ERROR] Недостаточно емкости! Требуется: {data_bits_needed}, доступно: {capacity}")
            return False
        
        data_bits = []
        for byte in data:
            for i in range(7, -1, -1):
                data_bits.append((byte >> i) & 1)
        
        positions = StegoModule.generate_positions(
            password, 
            img_array.shape, 
            len(data_bits)
        )
        
        stego_array = img_array.copy()
        for i, (y, x, channel) in enumerate(positions):
            if i < len(data_bits):
                original = stego_array[y, x, channel]
                new_value = (original & 0xFE) | data_bits[i]
                stego_array[y, x, channel] = new_value
        
        stego_img = Image.fromarray(stego_array)
        stego_img.save(output_path)
        print(f"[SUCCESS] Данные встроены в {output_path}")
        
        return True
    
    @staticmethod
    def extract_data_with_metadata(image_path: str, password: str, 
                                  expected_data_length: int = None) -> bytes:
        img = Image.open(image_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        img_array = np.array(img)
        
        positions_header = StegoModule.generate_positions(
            password, 
            img_array.shape, 
            64
        )
        
        header_bits = []
        for i, (y, x, channel) in enumerate(positions_header):
            if i >= 64:
                break
            pixel_val = img_array[y, x, channel]
            header_bits.append(pixel_val & 1)
        
        header_bytes = bytearray()
        for i in range(0, 64, 8):
            byte = 0
            for j in range(8):
                byte = (byte << 1) | header_bits[i + j]
            header_bytes.append(byte)
        
        header_bytes = bytes(header_bytes)
        
        try:
            payload_length, crc32_stored = struct.unpack('II', header_bytes[:8])
            
            total_data_length = 8 + payload_length
            total_bits_needed = total_data_length * 8
            
            all_positions = StegoModule.generate_positions(
                password, 
                img_array.shape, 
                total_bits_needed
            )
            
            all_bits = []
            for i, (y, x, channel) in enumerate(all_positions):
                if i >= total_bits_needed:
                    break
                pixel_val = img_array[y, x, channel]
                all_bits.append(pixel_val & 1)
            
            extracted_bytes = bytearray()
            for i in range(0, total_bits_needed, 8):
                if i + 8 > len(all_bits):
                    break
                byte = 0
                for j in range(8):
                    byte = (byte << 1) | all_bits[i + j]
                extracted_bytes.append(byte)
            
            return bytes(extracted_bytes)
            
        except struct.error as e:
            raise ValueError(f"Ошибка при чтении заголовка: {e}")
    
    @staticmethod
    def simple_lsb_embed(image_path: str, data: bytes, output_path: str) -> bool:
        img = Image.open(image_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        img_array = np.array(img)
        
        data_bits_needed = len(data) * 8
        capacity = StegoModule.calculate_capacity(img_array)
        
        if data_bits_needed > capacity:
            print(f"[ERROR] Недостаточно емкости для простого LSB!")
            return False
        
        data_bits = []
        for byte in data:
            for i in range(7, -1, -1):
                data_bits.append((byte >> i) & 1)
        
        stego_array = img_array.copy()
        flat_array = stego_array.flatten()
        
        for i in range(len(data_bits)):
            if i < len(flat_array):
                flat_array[i] = (flat_array[i] & 0xFE) | data_bits[i]
        
        stego_array = flat_array.reshape(img_array.shape)
        stego_img = Image.fromarray(stego_array)
        stego_img.save(output_path)
        
        return True