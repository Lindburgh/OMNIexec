import tkinter as tk
from tkinter import messagebox
import os
import subprocess
import math

HOME_DIR = os.path.expanduser("~")

class FileLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Pythonスクリプトランチャー")
        self.root.geometry("1000x600")
        self.current_dir = HOME_DIR

        self.launched_processes = []

        # 再起動ボタン
        button_restart = tk.Button(root, text="再起動", command=self.restart)
        button_restart.pack(pady=5)

        # 終了ボタン
        button_finish = tk.Button(root, text="終了", command=self.finish_scripts)
        button_finish.pack(pady=5)

        self.label = tk.Label(root, text=f"ディレクトリ: {self.current_dir}", font=("Arial", 20))
        self.label.pack(pady=10)

        # 2列表示用フレーム
        columns_frame = tk.Frame(root)
        columns_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # 左右のリストボックス
        self.listbox_left = tk.Listbox(columns_frame, font=("Arial", 20), width=30, height=20, selectmode=tk.SINGLE)
        self.listbox_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self.listbox_right = tk.Listbox(columns_frame, font=("Arial", 20), width=30, height=20, selectmode=tk.SINGLE)
        self.listbox_right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        # キーバインド（左右両方に）
        for lb in [self.listbox_left, self.listbox_right]:
            lb.bind("<Double-Button-1>", self.on_enter)
            lb.bind("<Return>", self.on_enter)
            lb.bind("<Up>", self.on_up_down)
            lb.bind("<Down>", self.on_up_down)

        self.active_listbox = self.listbox_left
        self.listbox_left.bind("<FocusIn>", lambda e: self.set_active_listbox(self.listbox_left))
        self.listbox_right.bind("<FocusIn>", lambda e: self.set_active_listbox(self.listbox_right))

        self.refresh_list()

    def set_active_listbox(self, lb):
        self.active_listbox = lb

    def refresh_list(self):
        self.listbox_left.delete(0, tk.END)
        self.listbox_right.delete(0, tk.END)
        items = os.listdir(self.current_dir)
        items.sort(key=lambda x: (not os.path.isdir(os.path.join(self.current_dir, x)), x.lower()))
        n = len(items)
        half = math.ceil(n / 2)
        left_items = items[:half]
        right_items = items[half:]

        for item in left_items:
            full_path = os.path.join(self.current_dir, item)
            if os.path.isdir(full_path):
                self.listbox_left.insert(tk.END, f"[フォルダ] {item}")
            else:
                self.listbox_left.insert(tk.END, f"{item}")
        for item in right_items:
            full_path = os.path.join(self.current_dir, item)
            if os.path.isdir(full_path):
                self.listbox_right.insert(tk.END, f"[フォルダ] {item}")
            else:
                self.listbox_right.insert(tk.END, f"{item}")

        self.label.config(text=f"ディレクトリ: {self.current_dir}")
        # 初期選択
        if self.listbox_left.size() > 0:
            self.listbox_left.select_set(0)
            self.listbox_left.focus_set()
            self.active_listbox = self.listbox_left
        elif self.listbox_right.size() > 0:
            self.listbox_right.select_set(0)
            self.listbox_right.focus_set()
            self.active_listbox = self.listbox_right

    def on_up_down(self, event):
        lb = self.active_listbox
        cur = lb.curselection()
        if not cur:
            lb.select_set(0)
            return
        idx = cur[0]
        if event.keysym == "Up" and idx > 0:
            lb.select_clear(idx)
            lb.select_set(idx - 1)
            lb.see(idx - 1)
        elif event.keysym == "Down" and idx < lb.size() - 1:
            lb.select_clear(idx)
            lb.select_set(idx + 1)
            lb.see(idx + 1)

    def on_enter(self, event):
        lb = self.active_listbox
        cur = lb.curselection()
        if not cur:
            return
        idx = cur[0]
        item_text = lb.get(idx)
        item_name = item_text.replace("[フォルダ] ", "")
        full_path = os.path.join(self.current_dir, item_name)
        if os.path.isdir(full_path):
            self.current_dir = full_path
            self.refresh_list()
        elif item_name.endswith(".py"):
            self.run_script(full_path)
        else:
            messagebox.showinfo("実行不可", "Pythonスクリプト（.py）以外は実行できません。")

    def run_script(self, script_path):
        try:
            process = subprocess.Popen(["python3", script_path], cwd=os.path.dirname(script_path))
            self.launched_processes.append(process)
            messagebox.showinfo("起動", f"{os.path.basename(script_path)} を起動しました。")
        except Exception as e:
            messagebox.showerror("エラー", f"起動できませんでした: {e}")

    def restart(self):
        import time
        applications_to_launch = [
            ["python3", "omni.py"],
        ]

        chat_dir = os.path.dirname(os.path.abspath(__file__))

        for i, app_command in enumerate(applications_to_launch):
            try:
                process = subprocess.Popen(app_command, cwd=chat_dir)
                self.launched_processes.append(process)
                if i == 0:
                    time.sleep(0)
            except FileNotFoundError:
                print(f"  エラー: コマンドまたはスクリプトが見つかりません: {app_command[0]}")
            except Exception as e:
                print(f"  起動エラー ({app_command[0]}): {e}")
        self.root.quit()

    def finish_scripts(self):
        finish_designated_scripts(self.launched_processes, self.root)

def finish_designated_scripts(launched_processes, root):
    for process in launched_processes:
        process.terminate()
    root.quit() # このプログラムで起動したスクリプトを終了させるための関数

if __name__ == "__main__":
    root = tk.Tk()
    app = FileLauncher(root)
    root.mainloop()