# -*- coding: utf-8 -*-
import os
import json
import sys
import subprocess
import platform
import threading
import tkinter as tk
from tkinter import messagebox, ttk
import pyperclip
from PIL import Image
import pystray
import difflib
from pynput import keyboard

# OS 판별
IS_WINDOWS = platform.system() == "Windows"

if IS_WINDOWS:
    import winreg
    REG_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
else:
    winreg = None
    REG_KEY = None

def get_app_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(os.path.abspath(sys.executable))
    else:
        return os.path.dirname(os.path.abspath(__file__))

APP_DIR = get_app_dir()
CONFIG_FILE = os.path.join(APP_DIR, "copycut_config.json")
APP_NAME = "CopyCut"

DEFAULT_FONT = "Malgun Gothic" if IS_WINDOWS else "Helvetica"

# 다국어 번역 리소스 팩 정의
LANG_PACK = {
    "ko": {
        "title": "카피컷 경로 변환 유틸리티 (copycut v1.05)",
        "guide_title": " 프로그램 작동 안내 ",
        "guide_desc": "이 프로그램이 켜져 있는 동안 단축키 [ Ctrl + Alt + O ] 를 누르면\n클립보드의 경로를 자동 분석하여 시스템 탐색기로 즉시 열어줍니다.\n(창을 닫으면 작업 표시줄 트레이 영역으로 최소화됩니다)",
        "rule_title": " 서버 매핑 규칙 설정 ",
        "mac_label": "맥 주소 패턴 (Mac) :",
        "win_label": "윈도우 드라이브 (Win) :",
        "btn_add": "➕ 규칙 추가",
        "btn_del": "🗑️ 선택 삭제",
        "history_title": " 최근 변환된 경로 히스토리 (항목 더블클릭 시 클립보드에 다시 복사) ",
        "btn_clear_hist": "기록 전체 비우기",
        "msg_input_error_title": "입력 오류",
        "msg_input_error_desc": "맥 패턴과 윈도우 드라이브 경로를 정확히 입력하세요.",
        "msg_dup_error_title": "중복 오류",
        "msg_dup_error_desc": "이미 등록된 주소 패턴입니다.",
        "msg_add_success_title": "완료",
        "msg_add_success_desc": "새로운 서버 매핑 규칙이 저장되었습니다.",
        "msg_del_error_title": "선택 오류",
        "msg_del_error_desc": "삭제할 규칙을 선택해 주세요.",
        "msg_last_rule_title": "확인",
        "msg_last_rule_desc": "마지막 매핑 규칙입니다. 삭제하시면 기본 변환이 작동하지 않을 수 있습니다. 정말 삭제하시겠습니까?",
        "msg_del_success_title": "완료",
        "msg_del_success_desc": "선택한 규칙이 삭제되었습니다.",
        "msg_copy_success_title": "복사 완료",
        "msg_copy_success_desc": "해당 경로가 클립보드에 다시 저장되었습니다.",
        "msg_clear_hist_title": "확인",
        "msg_clear_hist_desc": "최근 히스토리 기록을 전부 비우시겠습니까?",
        "tray_recent_title": "--- 최근 경로 (클릭 시 탐색기로 즉시 열기) ---",
        "tray_no_history": "최근 변환 경로 없음",
        "tray_start_boot": "부팅 시 자동 실행",
        "tray_open_win": "창 열기",
        "tray_exit": "종료",
        "tray_open_err": "트레이 오픈 에러"
    },
    "en": {
        "title": "CopyCut Path Conversion Utility (copycut v1.05)",
        "guide_title": " Program Operation Guide ",
        "guide_desc": "Press [ Ctrl + Alt + O ] while this program is running to analyze\nthe path in clipboard and open system File Explorer immediately.\n(Closing the window will minimize it to the system tray)",
        "rule_title": " Server Mapping Rules Configuration ",
        "mac_label": "Mac Address Pattern (Mac):",
        "win_label": "Windows Drive Path (Win):",
        "btn_add": "➕ Add Rule",
        "btn_del": "🗑️ Delete Selected",
        "history_title": " Recent Converted History (Double-click item to copy back to clipboard) ",
        "btn_clear_hist": "Clear All History",
        "msg_input_error_title": "Input Error",
        "msg_input_error_desc": "Please enter the Mac pattern and Windows drive path correctly.",
        "msg_dup_error_title": "Duplicate Error",
        "msg_dup_error_desc": "This address pattern is already registered.",
        "msg_add_success_title": "Completed",
        "msg_add_success_desc": "New server mapping rule has been saved.",
        "msg_del_error_title": "Selection Error",
        "msg_del_error_desc": "Please select a rule to delete.",
        "msg_last_rule_title": "Confirm",
        "msg_last_rule_desc": "This is the last mapping rule. Deleting it may cause basic conversion to fail. Are you sure you want to delete it?",
        "msg_del_success_title": "Completed",
        "msg_del_success_desc": "The selected rule has been deleted.",
        "msg_copy_success_title": "Copy Completed",
        "msg_copy_success_desc": "The path has been saved back to the clipboard.",
        "msg_clear_hist_title": "Confirm",
        "msg_clear_hist_desc": "Do you want to clear all recent history?",
        "tray_recent_title": "--- Recent Paths (Click to Open in Explorer) ---",
        "tray_no_history": "No Converted Paths Yet",
        "tray_start_boot": "Start on Boot",
        "tray_open_win": "Open Window",
        "tray_exit": "Exit",
        "tray_open_err": "Tray Open Error"
    },
    "zh": {
        "title": "CopyCut 路径转换工具 (copycut v1.05)",
        "guide_title": " 程序运行说明 ",
        "guide_desc": "在程序运行期间按下快捷键 [ Ctrl + Alt + O ] 将自动分析\n剪贴板中的路径并立即在系统资源管理器中打开。\n(关闭窗口会将程序最小化至系统托盘区域)",
        "rule_title": " 服务器映射规则设置 ",
        "mac_label": "麦克地址模式 (Mac):",
        "win_label": "Windows 驱动器 (Win):",
        "btn_add": "➕ 添加规则",
        "btn_del": "🗑️ 删除选中",
        "history_title": " 最近转换路径历史记录 (双击条目重新复制到剪贴板) ",
        "btn_clear_hist": "清空所有记录",
        "msg_input_error_title": "输入错误",
        "msg_input_error_desc": "请正确输入 Mac 模式和 Windows 驱动器路径。",
        "msg_dup_error_title": "重复错误",
        "msg_dup_error_desc": "该地址模式已注册。",
        "msg_add_success_title": "完成",
        "msg_add_success_desc": "新的服务器映射规则已保存。",
        "msg_del_error_title": "选择错误",
        "msg_del_error_desc": "请选择要删除的规则。",
        "msg_last_rule_title": "确认",
        "msg_last_rule_desc": "这是最后一条映射规则。删除后基本转换可能无法工作。确定要删除吗？",
        "msg_del_success_title": "完成",
        "msg_del_success_desc": "选中的规则已删除。",
        "msg_copy_success_title": "复制完成",
        "msg_copy_success_desc": "该路径已重新保存到剪贴板。",
        "msg_clear_hist_title": "确认",
        "msg_clear_hist_desc": "确定要清空所有最近的历史记录吗？",
        "tray_recent_title": "--- 最近路径 (点击在资源管理器中打开) ---",
        "tray_no_history": "暂无转换历史记录",
        "tray_start_boot": "开机自启动",
        "tray_open_win": "打开窗口",
        "tray_exit": "退出",
        "tray_open_err": "托盘打开错误"
    }
}

def get_resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def is_boot_start_enabled():
    if not IS_WINDOWS:
        return False
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_KEY, 0, winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(key, APP_NAME)
        winreg.CloseKey(key)
        return True
    except FileNotFoundError:
        return False
    except Exception:
        return False

def set_boot_start(enabled):
    if not IS_WINDOWS:
        return
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_KEY, 0, winreg.KEY_SET_VALUE)
        if enabled:
            if getattr(sys, 'frozen', False):
                app_path = os.path.abspath(sys.executable)
            else:
                app_path = os.path.abspath(sys.argv[0])
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, f'"{app_path}"')
        else:
            try:
                winreg.DeleteValue(key, APP_NAME)
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)
    except Exception as e:
        print(f"시작 프로그램 설정 오류: {e}")

def load_settings():
    # 이전 설정 파일 마이그레이션 지원
    old_config = os.path.join(APP_DIR, "antigravity_config.json")
    if not os.path.exists(CONFIG_FILE) and os.path.exists(old_config):
        try:
            with open(old_config, "r", encoding="utf-8") as f:
                old_data = json.load(f)
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(old_data, f, indent=4, ensure_ascii=False)
        except Exception:
            pass

    if not os.path.exists(CONFIG_FILE):
        default_data = {
            "mappings": [
                {"mac": "smb://10.115.1.20/projects/", "win": "Z:\\"}
            ],
            "history": [],
            "language": "ko"
        }
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(default_data, f, indent=4, ensure_ascii=False)
        except Exception:
            pass
        return default_data
    
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "language" not in data:
                data["language"] = "ko"
            return data
    except Exception:
        return {
            "mappings": [{"mac": "smb://10.115.1.20/projects/", "win": "Z:\\"}], 
            "history": [], 
            "language": "ko"
        }

def save_settings(data):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"설정 저장 실패: {e}")

def add_to_history(path):
    data = load_settings()
    history = data.get("history", [])
    
    if path in history:
        history.remove(path)
    history.insert(0, path)
    
    data["history"] = history[:10]
    save_settings(data)

def convert_path(raw_path):
    data = load_settings()
    mappings = data.get("mappings", [])
    
    target_path = raw_path.strip()
    target_path = target_path.strip('"').strip("'")
    
    # 윈도우용 백슬래시를 일단 비교 편의를 위해 슬래시로 변환하여 임시 저장
    norm_target = target_path.replace("\\", "/").strip()
    
    matched = False
    best_rule = None
    best_match_len = 0
    best_ratio = 0.0
    
    # 1단계: 완벽 매치 검사
    for rule in mappings:
        mac_prefix = rule["mac"].replace("\\", "/").strip()
        win_prefix = rule["win"].strip()
        
        # Mac 접두사 매치
        if norm_target.startswith(mac_prefix):
            best_rule = rule
            best_match_len = len(mac_prefix)
            matched = True
            break
        # Windows 드라이브 접두사 매치
        win_prefix_slash = win_prefix.replace("\\", "/")
        if norm_target.startswith(win_prefix_slash):
            best_rule = rule
            best_match_len = len(win_prefix)
            matched = True
            break

    # 2단계: 완벽 매칭이 실패한 경우, difflib 기반 유사도 매칭 시도 (85% 이상 일치율)
    if not matched:
        for rule in mappings:
            mac_prefix = rule["mac"].replace("\\", "/").strip()
            if not mac_prefix:
                continue
                
            mac_len = len(mac_prefix)
            target_len = len(norm_target)
            
            # 유사도 비교를 위해 접두사 길이의 1.3배 범위에서 검사 대상을 자름
            test_len = min(target_len, int(mac_len * 1.3))
            if test_len < int(mac_len * 0.5):
                continue
                
            target_prefix = norm_target[:test_len]
            
            # SequenceMatcher를 이용해 최적의 매칭 블록 탐색
            matcher = difflib.SequenceMatcher(None, mac_prefix, target_prefix)
            match_size = sum(block.size for block in matcher.get_matching_blocks() if block.size > 0)
            match_ratio = match_size / mac_len
            
            # 85% 이상 매칭되면서 이전보다 더 높은 일치율인 규칙을 우선순위로 선택
            if match_ratio >= 0.85 and match_ratio > best_ratio:
                best_ratio = match_ratio
                best_rule = rule
                
                # target_path에서 교체되어 날아가야 할 매칭 부분의 끝 인덱스를 구함
                matching_blocks = [b for b in matcher.get_matching_blocks() if b.size > 0]
                if matching_blocks:
                    last_block = max(matching_blocks, key=lambda b: b.b + b.size)
                    best_match_len = last_block.b + last_block.size
                else:
                    best_match_len = mac_len
                    
        if best_rule:
            matched = True

    # 변환 처리
    if matched and best_rule:
        mac_prefix = best_rule["mac"].strip()
        win_prefix = best_rule["win"].strip()
        
        # 윈도우 드라이브 경로로 들어온 경우, 단순히 경로 구분자만 변환
        win_prefix_slash = win_prefix.replace("\\", "/")
        if norm_target.startswith(win_prefix_slash):
            if IS_WINDOWS:
                target_path = target_path.replace("/", "\\")
            else:
                target_path = target_path.replace("\\", "/")
        else:
            # 매칭된 접두사 부분을 잘라내고 win_prefix로 치환
            remaining_path = target_path[best_match_len:]
            
            if win_prefix.endswith("\\") and remaining_path and remaining_path[0] in ["\\", "/"]:
                remaining_path = remaining_path[1:]
            elif win_prefix.endswith("/") and remaining_path and remaining_path[0] in ["\\", "/"]:
                remaining_path = remaining_path[1:]
            
            target_path = win_prefix + remaining_path
            
            if IS_WINDOWS:
                target_path = target_path.replace("/", "\\")
            else:
                target_path = target_path.replace("\\", "/")
    else:
        # 매칭되지 않은 경우라도 일반 폴더인 경우 슬래시 표준화
        if not target_path.startswith("http") and not target_path.startswith("smb:"):
            if IS_WINDOWS:
                target_path = target_path.replace("/", "\\")
            else:
                target_path = target_path.replace("\\", "/")
            
    # 중복 슬래시 축소 (OS에 맞춤)
    if IS_WINDOWS:
        while "\\\\" in target_path and not target_path.startswith("\\\\"):
            target_path = target_path.replace("\\\\", "\\")
    else:
        while "//" in target_path and not target_path.startswith("//"):
            target_path = target_path.replace("//", "/")
        
    return target_path

def smart_open_path():
    raw_path = pyperclip.paste().strip()
    if not raw_path:
        return

    target_path = convert_path(raw_path)
    
    if IS_WINDOWS:
        has_separator = any(c in target_path for c in ["\\", "/", ":"])
    else:
        has_separator = "/" in target_path

    if not has_separator:
        return

    original_target = target_path
    valid_path_found = False
    
    last_tried_path = ""

    while target_path and target_path != last_tried_path:
        if os.path.exists(target_path):
            valid_path_found = True
            break
        
        last_tried_path = target_path
        parent_path = os.path.dirname(target_path)
        
        if parent_path == target_path or parent_path is None:
            break
        target_path = parent_path

    if valid_path_found and target_path:
        try:
            normalized_path = os.path.abspath(target_path)
            
            if IS_WINDOWS:
                if os.path.isdir(normalized_path):
                    subprocess.Popen(f'explorer.exe "{normalized_path}"')
                else:
                    subprocess.Popen(f'explorer.exe /select,"{normalized_path}"')
            else:
                # macOS (Finder)
                if os.path.isdir(normalized_path):
                    subprocess.Popen(['open', normalized_path])
                else:
                    subprocess.Popen(['open', '-R', normalized_path])
                
            add_to_history(original_target)
            
            if 'app_instance' in globals() and app_instance:
                app_instance.refresh_all()
        except Exception as e:
            print(f"오픈 에러: {e}")
    else:
        print(f"존재하지 않는 경로: {original_target}")

def format_history_item(path):
    if len(path) > 50:
        return path[:25] + "..." + path[-25:]
    return path

class CopyCutApp:
    def __init__(self, root):
        self.root = root
        
        data = load_settings()
        self.current_lang = data.get("language", "ko")
        if self.current_lang not in LANG_PACK:
            self.current_lang = "ko"
            
        self.root.title(LANG_PACK[self.current_lang]["title"])
        self.root.geometry("620x550")
        self.root.resizable(False, False)
        
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        self.tray_icon = None
        self.create_widgets()
        self.refresh_all()
        
        self.setup_tray()
        
        self.root.after(500, self.check_privilege_hint)

    def create_widgets(self):
        lang_frame = ttk.Frame(self.root)
        lang_frame.pack(fill="x", padx=15, pady=(10, 0))
        
        self.lang_var = tk.StringVar(value=self.current_lang)
        ttk.Label(lang_frame, text="Language: ").pack(side="left")
        for lang_code, lang_name in [("ko", "한국어"), ("en", "English"), ("zh", "中文")]:
            ttk.Radiobutton(
                lang_frame, 
                text=lang_name, 
                value=lang_code, 
                variable=self.lang_var, 
                command=self.change_language
            ).pack(side="left", padx=5)

        self.info_frame = ttk.LabelFrame(self.root, padding=10)
        self.info_frame.pack(fill="x", padx=15, pady=5)
        
        self.guide_label = ttk.Label(
            self.info_frame, 
            font=(DEFAULT_FONT, 10, "bold"), 
            foreground="#0066cc", 
            justify="center"
        )
        self.guide_label.pack()

        self.mapping_frame = ttk.LabelFrame(self.root, padding=10)
        self.mapping_frame.pack(fill="both", expand=True, padx=15, pady=5)
        
        list_container = ttk.Frame(self.mapping_frame)
        list_container.pack(fill="both", expand=True, pady=5)
        
        self.scrollbar = ttk.Scrollbar(list_container, orient="vertical")
        self.mapping_listbox = tk.Listbox(
            list_container, yscrollcommand=self.scrollbar.set, 
            font=("Consolas", 10), selectmode=tk.SINGLE, height=5
        )
        self.scrollbar.config(command=self.mapping_listbox.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.mapping_listbox.pack(side="left", fill="both", expand=True)

        input_frame = ttk.Frame(self.mapping_frame)
        input_frame.pack(fill="x", pady=5)
        
        self.mac_label_widget = ttk.Label(input_frame)
        self.mac_label_widget.grid(row=0, column=0, sticky="w", pady=2)
        self.mac_entry = ttk.Entry(input_frame, width=35)
        self.mac_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        self.mac_entry.insert(0, "smb://10.115.1.20/projects/")

        self.win_label_widget = ttk.Label(input_frame)
        self.win_label_widget.grid(row=1, column=0, sticky="w", pady=2)
        self.win_entry = ttk.Entry(input_frame, width=35)
        self.win_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        self.win_entry.insert(0, "Z:\\" if IS_WINDOWS else "/Volumes/projects/")
        
        input_frame.columnconfigure(1, weight=1)

        self.btn_frame = ttk.Frame(self.mapping_frame)
        self.btn_frame.pack(fill="x", pady=5)
        
        self.add_btn = ttk.Button(self.btn_frame, command=self.add_rule)
        self.add_btn.pack(side="left", padx=5)
        
        self.del_btn = ttk.Button(self.btn_frame, command=self.delete_rule)
        self.del_btn.pack(side="left", padx=5)

        self.history_frame = ttk.LabelFrame(self.root, padding=10)
        self.history_frame.pack(fill="both", expand=True, padx=15, pady=5)
        
        self.history_listbox = tk.Listbox(self.history_frame, font=(DEFAULT_FONT, 9), height=6)
        self.history_listbox.pack(fill="both", expand=True)
        self.history_listbox.bind("<Double-1>", self.copy_history_to_clipboard)
        
        self.clear_btn = ttk.Button(self.history_frame, command=self.clear_history)
        self.clear_btn.pack(anchor="e", pady=3)

        self.update_ui_text()

    def change_language(self):
        self.current_lang = self.lang_var.get()
        data = load_settings()
        data["language"] = self.current_lang
        save_settings(data)
        
        self.update_ui_text()
        self.refresh_all()

    def update_ui_text(self):
        lp = LANG_PACK[self.current_lang]
        
        self.root.title(lp["title"])
        self.info_frame.config(text=lp["guide_title"])
        self.guide_label.config(text=lp["guide_desc"])
        self.mapping_frame.config(text=lp["rule_title"])
        self.mac_label_widget.config(text=lp["mac_label"])
        self.win_label_widget.config(text=lp["win_label"])
        self.add_btn.config(text=lp["btn_add"])
        self.del_btn.config(text=lp["btn_del"])
        self.history_frame.config(text=lp["history_title"])
        self.clear_btn.config(text=lp["btn_clear_hist"])

    def check_privilege_hint(self):
        print("CopyCut Path 단축키 감시 활성화 완료.")

    def refresh_all(self):
        self.mapping_listbox.delete(0, tk.END)
        self.history_listbox.delete(0, tk.END)
        
        data = load_settings()
        
        for idx, rule in enumerate(data.get("mappings", []), 1):
            self.mapping_listbox.insert(tk.END, f"[{idx}] {rule['mac']}  <--->  {rule['win']}")
            
        for path in data.get("history", []):
            self.history_listbox.insert(tk.END, path)
            
        if self.tray_icon:
            self.tray_icon.menu = self.create_tray_menu()

    def add_rule(self):
        lp = LANG_PACK[self.current_lang]
        mac_val = self.mac_entry.get().strip()
        win_val = self.win_entry.get().strip()
        
        if not mac_val or not win_val:
            messagebox.showwarning(lp["msg_input_error_title"], lp["msg_input_error_desc"])
            return
            
        data = load_settings()
        for rule in data["mappings"]:
            if rule["mac"] == mac_val:
                messagebox.showwarning(lp["msg_dup_error_title"], lp["msg_dup_error_desc"])
                return
                
        data["mappings"].append({"mac": mac_val, "win": win_val})
        save_settings(data)
        self.refresh_all()
        
        self.mac_entry.delete(0, tk.END)
        self.win_entry.delete(0, tk.END)
        messagebox.showinfo(lp["msg_add_success_title"], lp["msg_add_success_desc"])

    def delete_rule(self):
        lp = LANG_PACK[self.current_lang]
        selected = self.mapping_listbox.curselection()
        if not selected:
            messagebox.showwarning(lp["msg_del_error_title"], lp["msg_del_error_desc"])
            return
            
        idx = selected[0]
        data = load_settings()
        
        if len(data["mappings"]) <= 1:
            if not messagebox.askyesno(lp["msg_last_rule_title"], lp["msg_last_rule_desc"]):
                return
                
        del data["mappings"][idx]
        save_settings(data)
        self.refresh_all()
        messagebox.showinfo(lp["msg_del_success_title"], lp["msg_del_success_desc"])

    def copy_history_to_clipboard(self, event):
        lp = LANG_PACK[self.current_lang]
        selected = self.history_listbox.curselection()
        if not selected:
            return
        path = self.history_listbox.get(selected[0])
        pyperclip.copy(path)
        messagebox.showinfo(lp["msg_copy_success_title"], lp["msg_copy_success_desc"])

    def clear_history(self):
        lp = LANG_PACK[self.current_lang]
        if messagebox.askyesno(lp["msg_clear_hist_title"], lp["msg_clear_hist_desc"]):
            data = load_settings()
            data["history"] = []
            save_settings(data)
            self.refresh_all()

    # --- 트레이 아이콘 영역 ---
    def setup_tray(self):
        icon_file = get_resource_path("copycut_icon.ico")
        if os.path.exists(icon_file):
            image = Image.open(icon_file)
        else:
            image = Image.new("RGB", (64, 64), (0, 102, 204))
            
        self.tray_icon = pystray.Icon(
            "copycut", 
            image, 
            "CopyCut", 
            menu=self.create_tray_menu()
        )
        
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def create_tray_menu(self):
        data = load_settings()
        history = data.get("history", [])[:5]
        lp = LANG_PACK[self.current_lang]
        
        menu_items = []
        
        # 트레이 영역의 최근 경로 타이틀 및 목록 생성
        if history:
            menu_items.append(pystray.MenuItem(lp["tray_recent_title"], lambda: None, enabled=False))
            for path in history:
                formatted = format_history_item(path)
                menu_items.append(pystray.MenuItem(
                    formatted, 
                    lambda item, p=path: self.open_from_tray(p)
                ))
            menu_items.append(pystray.Menu.SEPARATOR)
        else:
            menu_items.append(pystray.MenuItem(lp["tray_no_history"], lambda: None, enabled=False))
            menu_items.append(pystray.Menu.SEPARATOR)
            
        # 부팅 시 자동 실행: 윈도우 환경에서만 메뉴 항목 노출
        if IS_WINDOWS:
            menu_items.append(pystray.MenuItem(
                lp["tray_start_boot"], 
                self.toggle_boot_start_menu, 
                checked=lambda item: is_boot_start_enabled()
            ))
        
        menu_items.append(pystray.MenuItem(lp["tray_open_win"], self.show_window, default=True))
        menu_items.append(pystray.MenuItem(lp["tray_exit"], self.quit_app))
        
        return pystray.Menu(*menu_items)

    def open_from_tray(self, raw_path):
        lp = LANG_PACK[self.current_lang]
        target_path = convert_path(raw_path)
        
        if IS_WINDOWS:
            has_separator = any(c in target_path for c in ["\\", "/", ":"])
        else:
            has_separator = "/" in target_path

        if not has_separator:
            return

        valid_path_found = False
        last_tried_path = ""

        # 하위 유효 폴더 추적 작동
        while target_path and target_path != last_tried_path:
            if os.path.exists(target_path):
                valid_path_found = True
                break
            
            last_tried_path = target_path
            parent_path = os.path.dirname(target_path)
            
            if parent_path == target_path or parent_path is None:
                break
            target_path = parent_path

        if valid_path_found and target_path:
            try:
                normalized_path = os.path.abspath(target_path)
                if IS_WINDOWS:
                    if os.path.isdir(normalized_path):
                        subprocess.Popen(f'explorer.exe "{normalized_path}"')
                    else:
                        subprocess.Popen(f'explorer.exe /select,"{normalized_path}"')
                else:
                    if os.path.isdir(normalized_path):
                        subprocess.Popen(['open', normalized_path])
                    else:
                        subprocess.Popen(['open', '-R', normalized_path])
            except Exception as e:
                print(f"트레이 오픈 에러: {e}")
                if self.tray_icon:
                    self.tray_icon.notify(lp["tray_open_err"], str(e))
        else:
            print(f"존재하지 않는 경로: {raw_path}")

    def toggle_boot_start_menu(self, icon, item):
        if IS_WINDOWS:
            current_state = is_boot_start_enabled()
            set_boot_start(not current_state)
            self.tray_icon.menu = self.create_tray_menu()

    def show_window(self):
        self.root.after(0, self._show_window_gui)

    def _show_window_gui(self):
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def hide_window(self):
        self.root.withdraw()

    def quit_app(self):
        if self.tray_icon:
            self.tray_icon.stop()
            
        global hotkey_listener
        if hotkey_listener:
            hotkey_listener.stop()
            
        self.root.after(0, self._destroy_gui)

    def _destroy_gui(self):
        self.root.destroy()
        sys.exit(0)

app_instance = None
hotkey_listener = None

if __name__ == "__main__":
    # pynput 비동기 글로벌 단축키 시작
    hotkey_listener = keyboard.GlobalHotKeys({
        '<ctrl>+<alt>+o': smart_open_path
    })
    hotkey_listener.start()
    
    root = tk.Tk()
    app_instance = CopyCutApp(root)
    
    root.protocol("WM_DELETE_WINDOW", app_instance.hide_window)
    root.mainloop()
