import os
import shutil
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import ctypes
import sys
import time
from pathlib import Path

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

class Del2000:
    def __init__(self, root):
        self.root = root
        self.root.title("Del2000 - Очиститель системы")
        self.root.geometry("600x550")
        self.root.resizable(False, False)
        
        self.bg_color = "#1e1e2f"
        self.fg_color = "#ffffff"
        self.accent_color = "#ff4757"
        self.secondary_color = "#2c2c3a"
        
        self.root.configure(bg=self.bg_color)
        self.cleaning_in_progress = False
        
        self.create_interface()
        
    def create_interface(self):
        title_frame = tk.Frame(self.root, bg=self.bg_color)
        title_frame.pack(pady=20)
        
        title_label = tk.Label(title_frame, text="🧹 Del2000", 
                               font=("Segoe UI", 28, "bold"),
                               bg=self.bg_color, fg=self.accent_color)
        title_label.pack()
        
        subtitle_label = tk.Label(title_frame, text="Очистка временных и ненужных файлов", 
                                  font=("Segoe UI", 10),
                                  bg=self.bg_color, fg=self.fg_color)
        subtitle_label.pack()
        
        main_frame = tk.Frame(self.root, bg=self.secondary_color, relief=tk.RAISED, bd=1)
        main_frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        
        warning_text = "Очищает временные файлы Windows\nКэш браузеров\nКорзину, временные папки\nИспользуйте на свой страх и риск"
        warning_label = tk.Label(main_frame, text=warning_text,
                                 font=("Segoe UI", 10),
                                 bg=self.secondary_color, fg="#ffa502",
                                 justify=tk.CENTER)
        warning_label.pack(pady=15)
        
        self.clean_btn = tk.Button(main_frame, text="🧹 ОЧИСТИТЬ 🧹",
                                   font=("Segoe UI", 14, "bold"),
                                   bg=self.accent_color, fg="white",
                                   activebackground="#ff6b81", activeforeground="white",
                                   bd=0, padx=30, pady=15,
                                   command=self.start_cleaning)
        self.clean_btn.pack(pady=15)
        
        log_frame = tk.Frame(main_frame, bg=self.secondary_color)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        log_label = tk.Label(log_frame, text="📋 Лог очистки:", 
                            bg=self.secondary_color, fg=self.fg_color,
                            font=("Segoe UI", 10, "bold"))
        log_label.pack(anchor=tk.W)
        
        self.log_area = scrolledtext.ScrolledText(log_frame, height=12,
                                                   bg="#2c2c3a", fg="#00ff9d",
                                                   font=("Consolas", 9),
                                                   wrap=tk.WORD)
        self.log_area.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.status_label = tk.Label(main_frame, text="✅ Готов к работе",
                                     bg=self.secondary_color, fg="#00ff9d",
                                     font=("Segoe UI", 9))
        self.status_label.pack(pady=5)
        
    def log(self, message, msg_type="info"):
        timestamp = time.strftime("%H:%M:%S")
        
        self.log_area.insert(tk.END, f"[{timestamp}] ", "timestamp")
        self.log_area.insert(tk.END, f"{message}\n", msg_type)
        self.log_area.see(tk.END)
        
        self.log_area.tag_config("timestamp", foreground="#888888")
        self.log_area.tag_config("info", foreground="#00ff9d")
        self.log_area.tag_config("warning", foreground="#ffa502")
        self.log_area.tag_config("error", foreground="#ff4757")
        self.log_area.tag_config("success", foreground="#00ff9d")
        
        self.root.update()
    
    def delete_file(self, path):
        try:
            if os.path.isfile(path):
                os.remove(path)
                return True
            elif os.path.isdir(path):
                shutil.rmtree(path, ignore_errors=False)
                return True
        except:
            pass
        return False
    
    def clean_folder(self, folder, description):
        if not os.path.exists(folder):
            return 0
        
        self.log(f"  {description}: {folder}", "info")
        deleted = 0
        try:
            for item in os.listdir(folder):
                item_path = os.path.join(folder, item)
                if self.delete_file(item_path):
                    deleted += 1
                    if deleted % 500 == 0:
                        self.log(f"    Удалено {deleted} объектов...", "info")
        except Exception as e:
            self.log(f"    Ошибка доступа: {e}", "error")
        
        if deleted > 0:
            self.log(f"    ✓ Удалено {deleted} объектов", "success")
        return deleted
    
    def clean_windows_temp(self):
        return self.clean_folder("C:\\Windows\\Temp", "Системные временные")
    
    def clean_user_temp(self):
        return self.clean_folder(os.path.expandvars("%LOCALAPPDATA%\\Temp"), "Пользовательские временные")
    
    def clean_prefetch(self):
        return self.clean_folder("C:\\Windows\\Prefetch", "Prefetch")
    
    def clean_recycle_bin(self):
        deleted = 0
        for drive in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            recycle = f"{drive}:\\$Recycle.Bin"
            if os.path.exists(recycle):
                try:
                    for item in os.listdir(recycle):
                        item_path = os.path.join(recycle, item)
                        if self.delete_file(item_path):
                            deleted += 1
                except:
                    pass
        if deleted > 0:
            self.log(f"  Корзина: ✓ Удалено {deleted} объектов", "success")
        return deleted
    
    def clean_browser_cache(self):
        """Безопасная очистка кэша браузеров (НЕ трогает куки и пароли)"""
        total = 0
        
        chrome_profile = os.path.expandvars("%LOCALAPPDATA%\\Google\\Chrome\\User Data\\Default")
        if os.path.exists(chrome_profile):
            safe_folders = ["Cache", "Code Cache", "Service Worker"]
            for folder in safe_folders:
                folder_path = os.path.join(chrome_profile, folder)
                total += self.clean_folder(folder_path, f"Chrome {folder}")
        
        edge_profile = os.path.expandvars("%LOCALAPPDATA%\\Microsoft\\Edge\\User Data\\Default")
        if os.path.exists(edge_profile):
            safe_folders = ["Cache", "Code Cache"]
            for folder in safe_folders:
                folder_path = os.path.join(edge_profile, folder)
                total += self.clean_folder(folder_path, f"Edge {folder}")
        
        firefox_profiles = os.path.expandvars("%APPDATA%\\Mozilla\\Firefox\\Profiles")
        if os.path.exists(firefox_profiles):
            try:
                for profile in os.listdir(firefox_profiles):
                    profile_path = os.path.join(firefox_profiles, profile)
                    if os.path.isdir(profile_path):
                        cache_folder = os.path.join(profile_path, "cache2")
                        total += self.clean_folder(cache_folder, "Firefox Cache")
                        startup_cache = os.path.join(profile_path, "startupCache")
                        total += self.clean_folder(startup_cache, "Firefox StartupCache")
            except:
                pass
        
        opera_cache = os.path.expandvars("%LOCALAPPDATA%\\Opera Software\\Opera Stable\\Cache")
        total += self.clean_folder(opera_cache, "Opera Cache")
        
        return total
    
    def clean_recent_files(self):
        recent = os.path.expandvars("%APPDATA%\\Microsoft\\Windows\\Recent")
        return self.clean_folder(recent, "Недавние документы")
    
    def clean_temp_office(self):
        office_temp = os.path.expandvars("%LOCALAPPDATA%\\Microsoft\\Office\\16.0\\OfficeFileCache")
        return self.clean_folder(office_temp, "Office Cache")
    
    def clean_downloads_temp(self):
        downloads_folder = os.path.expandvars("%USERPROFILE%\\Downloads")
        deleted = 0
        try:
            for item in os.listdir(downloads_folder):
                if item.endswith('.tmp') or item.endswith('.temp'):
                    item_path = os.path.join(downloads_folder, item)
                    if self.delete_file(item_path):
                        deleted += 1
        except:
            pass
        if deleted > 0:
            self.log(f"  Временные файлы в Downloads: ✓ Удалено {deleted} файлов", "success")
        return deleted
    
    def clean_thread(self):
        self.cleaning_in_progress = True
        self.clean_btn.config(state=tk.DISABLED, text="🧹 ОЧИСТКА... 🧹")
        self.status_label.config(text="🔄 Выполняется очистка...", fg="#ffa502")
        
        try:
            self.log("="*50, "info")
            self.log("НАЧАЛО ОЧИСТКИ", "info")
            self.log("="*50, "info")
            
            total = 0
            
            total += self.clean_windows_temp()
            total += self.clean_user_temp()
            total += self.clean_prefetch()
            total += self.clean_recycle_bin()
            
            self.log("\n🌐 Браузеры (только кэш, пароли не трогаем):", "info")
            total += self.clean_browser_cache()
            
            self.log("\n📁 Дополнительно:", "info")
            total += self.clean_recent_files()
            total += self.clean_temp_office()
            total += self.clean_downloads_temp()
            
            self.log("\n" + "="*50, "info")
            self.log(f"✅ ОЧИСТКА ЗАВЕРШЕНА!", "success")
            self.log(f"📊 ВСЕГО УДАЛЕНО: {total} ОБЪЕКТОВ", "success")
            self.log("="*50, "info")
            
            self.status_label.config(text=f"✅ Удалено {total} объектов", fg="#00ff9d")
            
            messagebox.showinfo("Del2000", f"Очистка завершена!\n\nУдалено {total} временных файлов и мусора.\n\nПароли и вход на сайты сохранены ✅")
            
        except Exception as e:
            self.log(f"❌ Критическая ошибка: {e}", "error")
            self.status_label.config(text="❌ Ошибка при очистке", fg="#ff4757")
            messagebox.showerror("Ошибка", f"Произошла ошибка:\n{e}")
        
        finally:
            self.cleaning_in_progress = False
            self.clean_btn.config(state=tk.NORMAL, text="🧹 ОЧИСТИТЬ 🧹")
    
    def start_cleaning(self):
        if self.cleaning_in_progress:
            messagebox.showwarning("Внимание", "Очистка уже выполняется!")
            return
        
        if not is_admin():
            result = messagebox.askyesno("Права администратора",
                "Для очистки системных папок требуются права администратора.\n\n"
                "Запустить программу с правами администратора?")
            if result:
                run_as_admin()
                return
        
        result = messagebox.askyesno("Подтверждение",
            "Будут очищены:\n\n"
            "✓ Системные временные файлы\n"
            "✓ Пользовательские временные файлы\n"
            "✓ Кэш запуска программ\n"
            "✓ Корзина\n"
            "✓ Кэш браузеров\n"
            "✓ Недавние документы\n"
            "✓ Временные файлы Office\n"
            "Продолжить?",
            icon='warning')
        
        if result:
            threading.Thread(target=self.clean_thread, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = Del2000(root)
    root.mainloop()