import hashlib
import struct
import zlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

class CryptoModule:
    @staticmethod
    def derive_key(password: str, key_length: int = 16) -> bytes:
        salt = b'fixed_salt_lab3'
        key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000, key_length)
        return key
    
    @staticmethod
    def prepare_data_for_embedding(message: str, password: str) -> bytes:
        key = CryptoModule.derive_key(password)
        
        iv = get_random_bytes(16)
        
        cipher = AES.new(key, AES.MODE_CBC, iv)
        ciphertext = cipher.encrypt(pad(message.encode(), AES.block_size))
        
        payload = iv + ciphertext
        payload_length = len(payload)
        
        crc32_value = zlib.crc32(payload) & 0xFFFFFFFF

        data_to_embed = struct.pack('II', payload_length, crc32_value) + payload
        
        return data_to_embed
    
    @staticmethod
    def extract_and_decrypt(data: bytes, password: str) -> str:
        if len(data) < 8:
            raise ValueError("Некорректные данные: слишком короткие")
        
        payload_length, crc32_stored = struct.unpack('II', data[:8])
        
        if len(data) < 8 + payload_length:
            raise ValueError(f"Некорректные данные: ожидалось {payload_length} байт, получено {len(data)-8}")
        
        payload = data[8:8 + payload_length]
        
        crc32_calculated = zlib.crc32(payload) & 0xFFFFFFFF
        if crc32_calculated != crc32_stored:
            raise ValueError(f"Ошибка целостности данных: CRC32 mismatch "
                           f"(ожидалось {crc32_stored:08x}, "
                           f"получено {crc32_calculated:08x})")
        
        iv = payload[:16]
        ciphertext = payload[16:]
        
        key = CryptoModule.derive_key(password)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted = unpad(cipher.decrypt(ciphertext), AES.block_size)
        
        return decrypted.decode()