import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import seaborn as sns

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
        
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        
        diff_img_simple = np.sum(original != simple, axis=2) > 0
        
        im1 = axes[0].imshow(diff_img_simple, cmap='Reds', aspect='auto')
        axes[0].set_title("Простой LSB", fontsize=14, fontweight='bold', pad=15)
        axes[0].axis('off')
        
        diff_img_hybrid = np.sum(original != hybrid, axis=2) > 0
        
        im2 = axes[1].imshow(diff_img_hybrid, cmap='Blues', aspect='auto')
        axes[1].set_title("Гибридный метод", fontsize=14, fontweight='bold', pad=15)
        axes[1].axis('off')
        
        axes[0].text(0.5, -0.05, f'Изменено пикселей: {diff_simple:,} ({diff_simple/original.size*100:.1f}%)', 
                    transform=axes[0].transAxes, ha='center', fontsize=11, fontweight='bold')
        axes[1].text(0.5, -0.05, f'Изменено пикселей: {diff_hybrid:,} ({diff_hybrid/original.size*100:.1f}%)', 
                    transform=axes[1].transAxes, ha='center', fontsize=11, fontweight='bold')
        
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='white', edgecolor='black', label='Без изменений'),
            Patch(facecolor='red', edgecolor='black', label='Изменен (Простой LSB)'),
            Patch(facecolor='blue', edgecolor='black', label='Изменен (Гибридный)')
        ]
        
        fig.legend(handles=legend_elements, loc='upper center', 
                  bbox_to_anchor=(0.5, 0.95), ncol=3, fontsize=11)
        
        plt.suptitle('Сравнение методов стеганографии: Измененные пиксели', 
                    fontsize=16, fontweight='bold', y=1.0)
        
        plt.tight_layout(rect=[0, 0, 1, 0.92])
        plt.savefig('result/hotmap.png', dpi=150, bbox_inches='tight')
        plt.show()
        
        return {
            'psnr_simple': psnr_simple,
            'psnr_hybrid': psnr_hybrid,
            'changed_pixels_simple': diff_simple,
            'changed_pixels_hybrid': diff_hybrid
        }