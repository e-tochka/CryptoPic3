import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

class AnalysisModule:
    @staticmethod
    def calculate_psnr(original: np.ndarray, stego: np.ndarray):
        mse = np.mean((original - stego) ** 2)
        if mse == 0:
            return float('inf')
        max_pixel = 255.0
        psnr = 20 * np.log10(max_pixel / np.sqrt(mse))
        return psnr
    
    @staticmethod
    def compare_methods(original_path: str, simple_path: str, hybrid_path: str):
        original = np.array(Image.open(original_path))
        simple = np.array(Image.open(simple_path))
        hybrid = np.array(Image.open(hybrid_path))
        
        psnr_simple = AnalysisModule.calculate_psnr(original, simple)
        psnr_hybrid = AnalysisModule.calculate_psnr(original, hybrid)
        
        diff_simple = np.sum(original != simple) / 3
        diff_hybrid = np.sum(original != hybrid) / 3
        
        original_lsb = original.flatten() & 1
        simple_lsb = simple.flatten() & 1
        hybrid_lsb = hybrid.flatten() & 1
        
        print("=== Сравнение методов ===")
        print(f"PSNR простой LSB: {psnr_simple:.2f} dB")
        print(f"PSNR гибридный: {psnr_hybrid:.2f} dB")
        print(f"Измененных пикселей (простой): {diff_simple}")
        print(f"Измененных пикселей (гибридный): {diff_hybrid}")
        print(f"Изменено {diff_simple / original.size * 100:.2f}% пикселей (простой)")
        print(f"Изменено {diff_hybrid / original.size * 100:.2f}% пикселей (гибридный)")
        
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        
        axes[0, 0].imshow(original)
        axes[0, 0].set_title("Оригинал")
        axes[0, 0].axis('off')
        

        axes[0, 1].imshow(simple)
        axes[0, 1].set_title("Простой LSB")
        axes[0, 1].axis('off')
        
        axes[0, 2].imshow(hybrid)
        axes[0, 2].set_title("Гибридный метод")
        axes[0, 2].axis('off')
        
        diff_img_simple = np.sum(np.abs(original - simple), axis=2)
        diff_img_hybrid = np.sum(np.abs(original - hybrid), axis=2)
        
        axes[1, 0].imshow(diff_img_simple, cmap='hot')
        axes[1, 0].set_title("Разность (простой)")
        axes[1, 0].axis('off')
        
        axes[1, 1].imshow(diff_img_hybrid, cmap='hot')
        axes[1, 1].set_title("Разность (гибридный)")
        axes[1, 1].axis('off')
        
        axes[1, 2].hist([original_lsb, simple_lsb, hybrid_lsb], 
                       label=['Оригинал', 'Простой', 'Гибрид'], alpha=0.7)
        axes[1, 2].set_title("Распределение LSB")
        axes[1, 2].legend()
        axes[1, 2].set_xlabel("Значение LSB")
        axes[1, 2].set_ylabel("Частота")
        
        plt.tight_layout()
        plt.savefig('comparison_results.png')
        plt.show()
        
        return {
            'psnr_simple': psnr_simple,
            'psnr_hybrid': psnr_hybrid,
            'changed_pixels_simple': diff_simple,
            'changed_pixels_hybrid': diff_hybrid
        }