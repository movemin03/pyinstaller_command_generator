import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import threading
import json
import ast
import shutil
from datetime import datetime
import time


class PyInstallerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PyInstaller GUI - 종합 도구")
        self.root.geometry("900x700")

        # 기본 바탕화면 경로 설정
        self.desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")

        # 설정 저장을 위한 변수들
        self.config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pyinstaller_gui_config.json")
        self.recent_projects = []

        # 메인 노트북 (탭 컨테이너) 생성
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 탭 생성
        self.create_basic_tab()
        self.create_advanced_tab()
        self.create_hooks_tab()
        self.create_platform_tab()
        self.create_execution_tab()

        # 상태 바 생성
        self.status_bar = ttk.Label(root, text="준비됨", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # 설정 로드
        self.load_config()

    def create_basic_tab(self):
        """기본 설정 탭 생성"""
        self.tab_basic = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_basic, text="기본 설정")

        # 스크롤 가능한 프레임 생성
        canvas = tk.Canvas(self.tab_basic)
        scrollbar = ttk.Scrollbar(self.tab_basic, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 최근 프로젝트 프레임
        recent_frame = ttk.LabelFrame(scrollable_frame, text="최근 프로젝트")
        recent_frame.pack(fill=tk.X, padx=10, pady=5)

        self.recent_combo = ttk.Combobox(recent_frame, width=50)
        self.recent_combo.pack(side=tk.LEFT, padx=5, pady=5)

        load_btn = ttk.Button(recent_frame, text="불러오기", command=self.load_recent_project)
        load_btn.pack(side=tk.LEFT, padx=5, pady=5)

        # 파일 경로 프레임
        file_frame = ttk.LabelFrame(scrollable_frame, text="Python 파일")
        file_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(file_frame, text="Python 파일 경로:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.script_path = tk.StringVar()
        self.script_path.trace_add("write", self.on_script_path_change)
        script_entry = ttk.Entry(file_frame, textvariable=self.script_path, width=50)
        script_entry.grid(row=0, column=1, padx=5, pady=5)

        browse_btn = ttk.Button(file_frame, text="찾아보기", command=self.browse_script)
        browse_btn.grid(row=0, column=2, padx=5, pady=5)

        # 출력 설정 프레임
        output_frame = ttk.LabelFrame(scrollable_frame, text="출력 설정")
        output_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(output_frame, text="앱 이름:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.app_name = tk.StringVar()
        name_entry = ttk.Entry(output_frame, textvariable=self.app_name, width=50)
        name_entry.grid(row=0, column=1, columnspan=2, padx=5, pady=5)

        ttk.Label(output_frame, text="출력 폴더:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.output_dir = tk.StringVar(value=self.desktop_path)
        output_entry = ttk.Entry(output_frame, textvariable=self.output_dir, width=50)
        output_entry.grid(row=1, column=1, padx=5, pady=5)

        output_btn = ttk.Button(output_frame, text="찾아보기", command=self.browse_output_dir)
        output_btn.grid(row=1, column=2, padx=5, pady=5)

        ttk.Label(output_frame, text="작업 폴더:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.work_dir = tk.StringVar()
        work_entry = ttk.Entry(output_frame, textvariable=self.work_dir, width=50)
        work_entry.grid(row=2, column=1, padx=5, pady=5)

        work_btn = ttk.Button(output_frame, text="찾아보기", command=self.browse_work_dir)
        work_btn.grid(row=2, column=2, padx=5, pady=5)

        # 빌드 타입 프레임
        build_frame = ttk.LabelFrame(scrollable_frame, text="빌드 타입")
        build_frame.pack(fill=tk.X, padx=10, pady=5)

        self.build_type = tk.StringVar(value="--onedir")
        ttk.Radiobutton(build_frame, text="디렉토리로 빌드 (--onedir)", variable=self.build_type,
                        value="--onedir").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Radiobutton(build_frame, text="단일 파일로 빌드 (--onefile)", variable=self.build_type,
                        value="--onefile").grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

        # 콘솔 옵션 프레임
        console_frame = ttk.LabelFrame(scrollable_frame, text="콘솔 옵션")
        console_frame.pack(fill=tk.X, padx=10, pady=5)

        self.console_option = tk.StringVar(value="--console")
        ttk.Radiobutton(console_frame, text="콘솔 표시 (--console)", variable=self.console_option,
                        value="--console").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Radiobutton(console_frame, text="콘솔 숨김 (--noconsole)", variable=self.console_option,
                        value="--noconsole").grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

        # 일반 옵션 프레임
        general_frame = ttk.LabelFrame(scrollable_frame, text="일반 옵션")
        general_frame.pack(fill=tk.X, padx=10, pady=5)

        self.clean_build = tk.BooleanVar(value=False)
        ttk.Checkbutton(general_frame, text="빌드 전 캐시 정리 (--clean)",
                        variable=self.clean_build).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)

        self.no_confirm = tk.BooleanVar(value=False)
        ttk.Checkbutton(general_frame, text="확인 없이 덮어쓰기 (--noconfirm)",
                        variable=self.no_confirm).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

        # 로그 레벨 프레임
        log_frame = ttk.LabelFrame(scrollable_frame, text="로그 레벨")
        log_frame.pack(fill=tk.X, padx=10, pady=5)

        self.log_level = tk.StringVar(value="INFO")
        log_levels = ["TRACE", "DEBUG", "INFO", "WARN", "ERROR", "CRITICAL"]
        ttk.Label(log_frame, text="로그 레벨:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        log_combo = ttk.Combobox(log_frame, textvariable=self.log_level, values=log_levels, state="readonly")
        log_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

    def on_script_path_change(self, *args):
        """파일 경로가 변경될 때 호출되는 콜백"""
        file_path = self.script_path.get()
        if file_path and os.path.isfile(file_path) and file_path.endswith('.py'):
            # 경로가 유효한 Python 파일인 경우에만 분석 실행
            self.analyze_and_add_imports(file_path)

    def create_advanced_tab(self):
        """고급 설정 탭 생성"""
        self.tab_advanced = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_advanced, text="고급 설정")

        # 스크롤 가능한 프레임 생성
        canvas = tk.Canvas(self.tab_advanced)
        scrollbar = ttk.Scrollbar(self.tab_advanced, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # UPX 설정 프레임
        upx_frame = ttk.LabelFrame(scrollable_frame, text="UPX 압축 설정")
        upx_frame.pack(fill=tk.X, padx=10, pady=5)

        self.use_upx = tk.BooleanVar(value=True)
        ttk.Checkbutton(upx_frame, text="UPX 압축 사용", variable=self.use_upx).grid(row=0, column=0, sticky=tk.W, padx=5,
                                                                                 pady=5)

        ttk.Label(upx_frame, text="UPX 경로:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.upx_dir = tk.StringVar()
        upx_entry = ttk.Entry(upx_frame, textvariable=self.upx_dir, width=50)
        upx_entry.grid(row=1, column=1, padx=5, pady=5)

        upx_btn = ttk.Button(upx_frame, text="찾아보기", command=self.browse_upx_dir)
        upx_btn.grid(row=1, column=2, padx=5, pady=5)

        # 데이터 파일 프레임
        data_frame = ttk.LabelFrame(scrollable_frame, text="데이터 파일 추가")
        data_frame.pack(fill=tk.X, padx=10, pady=5)

        self.data_files = []
        self.data_listbox = tk.Listbox(data_frame, width=60, height=5)
        self.data_listbox.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky=tk.W + tk.E)

        add_data_btn = ttk.Button(data_frame, text="추가", command=self.add_data_file)
        add_data_btn.grid(row=1, column=0, padx=5, pady=5)

        remove_data_btn = ttk.Button(data_frame, text="제거", command=self.remove_data_file)
        remove_data_btn.grid(row=1, column=1, padx=5, pady=5)

        # 바이너리 파일 프레임
        binary_frame = ttk.LabelFrame(scrollable_frame, text="바이너리 파일 추가")
        binary_frame.pack(fill=tk.X, padx=10, pady=5)

        self.binary_files = []
        self.binary_listbox = tk.Listbox(binary_frame, width=60, height=5)
        self.binary_listbox.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky=tk.W + tk.E)

        add_binary_btn = ttk.Button(binary_frame, text="추가", command=self.add_binary_file)
        add_binary_btn.grid(row=1, column=0, padx=5, pady=5)

        remove_binary_btn = ttk.Button(binary_frame, text="제거", command=self.remove_binary_file)
        remove_binary_btn.grid(row=1, column=1, padx=5, pady=5)

        # 고급 옵션 프레임
        adv_options_frame = ttk.LabelFrame(scrollable_frame, text="고급 옵션")
        adv_options_frame.pack(fill=tk.X, padx=10, pady=5)

        self.strip = tk.BooleanVar(value=False)
        ttk.Checkbutton(adv_options_frame, text="실행 파일 스트립 (--strip)",
                        variable=self.strip).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)

        self.noupx = tk.BooleanVar(value=False)
        ttk.Checkbutton(adv_options_frame, text="UPX 사용 안함 (--noupx)",
                        variable=self.noupx).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

        self.ascii = tk.BooleanVar(value=False)
        ttk.Checkbutton(adv_options_frame, text="ASCII 전용 (--ascii)",
                        variable=self.ascii).grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)

        self.uac_admin = tk.BooleanVar(value=False)
        ttk.Checkbutton(adv_options_frame, text="관리자 권한 요청 (--uac-admin)",
                        variable=self.uac_admin).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

        self.uac_uiaccess = tk.BooleanVar(value=False)
        ttk.Checkbutton(adv_options_frame, text="UI 접근 권한 (--uac-uiaccess)",
                        variable=self.uac_uiaccess).grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)

        self.win_private_assemblies = tk.BooleanVar(value=False)
        ttk.Checkbutton(adv_options_frame, text="Private Assemblies (--win-private-assemblies)",
                        variable=self.win_private_assemblies).grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)

        self.win_no_prefer_redirects = tk.BooleanVar(value=False)
        ttk.Checkbutton(adv_options_frame, text="No Prefer Redirects (--win-no-prefer-redirects)",
                        variable=self.win_no_prefer_redirects).grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)

    def create_hooks_tab(self):
        """훅 및 임포트 탭 생성"""
        self.tab_hooks = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_hooks, text="훅 및 임포트")

        # 스크롤 가능한 프레임 생성
        canvas = tk.Canvas(self.tab_hooks)
        scrollbar = ttk.Scrollbar(self.tab_hooks, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 숨겨진 임포트 프레임
        hidden_frame = ttk.LabelFrame(scrollable_frame, text="숨겨진 임포트 (--hidden-import)")
        hidden_frame.pack(fill=tk.X, padx=10, pady=5)

        self.hidden_imports = []
        self.hidden_listbox = tk.Listbox(hidden_frame, width=60, height=5)
        self.hidden_listbox.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky=tk.W + tk.E)

        ttk.Label(hidden_frame, text="모듈 이름:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.hidden_import_entry = ttk.Entry(hidden_frame, width=40)
        self.hidden_import_entry.grid(row=1, column=1, padx=5, pady=5)

        add_hidden_btn = ttk.Button(hidden_frame, text="추가", command=self.add_hidden_import)
        add_hidden_btn.grid(row=1, column=2, padx=5, pady=5)

        remove_hidden_btn = ttk.Button(hidden_frame, text="제거", command=self.remove_hidden_import)
        remove_hidden_btn.grid(row=2, column=0, padx=5, pady=5)

        analyze_btn = ttk.Button(hidden_frame, text="파일 분석", command=self.analyze_imports)
        analyze_btn.grid(row=2, column=1, padx=5, pady=5)

        # 제외할 모듈 프레임
        exclude_frame = ttk.LabelFrame(scrollable_frame, text="제외할 모듈 (--exclude-module)")
        exclude_frame.pack(fill=tk.X, padx=10, pady=5)

        self.exclude_modules = []
        self.exclude_listbox = tk.Listbox(exclude_frame, width=60, height=5)
        self.exclude_listbox.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky=tk.W + tk.E)

        ttk.Label(exclude_frame, text="모듈 이름:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.exclude_module_entry = ttk.Entry(exclude_frame, width=40)
        self.exclude_module_entry.grid(row=1, column=1, padx=5, pady=5)

        add_exclude_btn = ttk.Button(exclude_frame, text="추가", command=self.add_exclude_module)
        add_exclude_btn.grid(row=1, column=2, padx=5, pady=5)

        remove_exclude_btn = ttk.Button(exclude_frame, text="제거", command=self.remove_exclude_module)
        remove_exclude_btn.grid(row=2, column=0, padx=5, pady=5)

        # 추가 훅 디렉토리 프레임
        hooks_dir_frame = ttk.LabelFrame(scrollable_frame, text="추가 훅 디렉토리 (--additional-hooks-dir)")
        hooks_dir_frame.pack(fill=tk.X, padx=10, pady=5)

        self.hooks_dirs = []
        self.hooks_dir_listbox = tk.Listbox(hooks_dir_frame, width=60, height=5)
        self.hooks_dir_listbox.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky=tk.W + tk.E)

        add_hooks_dir_btn = ttk.Button(hooks_dir_frame, text="디렉토리 추가", command=self.add_hooks_dir)
        add_hooks_dir_btn.grid(row=1, column=0, padx=5, pady=5)

        remove_hooks_dir_btn = ttk.Button(hooks_dir_frame, text="제거", command=self.remove_hooks_dir)
        remove_hooks_dir_btn.grid(row=1, column=1, padx=5, pady=5)

        # 런타임 훅 프레임
        runtime_hook_frame = ttk.LabelFrame(scrollable_frame, text="런타임 훅 (--runtime-hook)")
        runtime_hook_frame.pack(fill=tk.X, padx=10, pady=5)

        self.runtime_hooks = []
        self.runtime_hook_listbox = tk.Listbox(runtime_hook_frame, width=60, height=5)
        self.runtime_hook_listbox.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky=tk.W + tk.E)

        add_runtime_hook_btn = ttk.Button(runtime_hook_frame, text="파일 추가", command=self.add_runtime_hook)
        add_runtime_hook_btn.grid(row=1, column=0, padx=5, pady=5)

        remove_runtime_hook_btn = ttk.Button(runtime_hook_frame, text="제거", command=self.remove_runtime_hook)
        remove_runtime_hook_btn.grid(row=1, column=1, padx=5, pady=5)

    def create_platform_tab(self):
        """플랫폼 특화 옵션 탭 생성"""
        self.tab_platform = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_platform, text="플랫폼 옵션")

        # 스크롤 가능한 프레임 생성
        canvas = tk.Canvas(self.tab_platform)
        scrollbar = ttk.Scrollbar(self.tab_platform, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Windows 특화 옵션 프레임
        win_frame = ttk.LabelFrame(scrollable_frame, text="Windows 특화 옵션")
        win_frame.pack(fill=tk.X, padx=10, pady=5)

        # 아이콘 설정
        ttk.Label(win_frame, text="아이콘 파일 (.ico):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.icon_file = tk.StringVar()
        icon_entry = ttk.Entry(win_frame, textvariable=self.icon_file, width=50)
        icon_entry.grid(row=0, column=1, padx=5, pady=5)

        icon_btn = ttk.Button(win_frame, text="찾아보기", command=self.browse_icon)
        icon_btn.grid(row=0, column=2, padx=5, pady=5)

        # 버전 파일 설정
        ttk.Label(win_frame, text="버전 파일:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.version_file = tk.StringVar()
        version_entry = ttk.Entry(win_frame, textvariable=self.version_file, width=50)
        version_entry.grid(row=1, column=1, padx=5, pady=5)

        version_btn = ttk.Button(win_frame, text="찾아보기", command=self.browse_version_file)
        version_btn.grid(row=1, column=2, padx=5, pady=5)

        # 매니페스트 파일 설정
        ttk.Label(win_frame, text="매니페스트 파일:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.manifest_file = tk.StringVar()
        manifest_entry = ttk.Entry(win_frame, textvariable=self.manifest_file, width=50)
        manifest_entry.grid(row=2, column=1, padx=5, pady=5)

        manifest_btn = ttk.Button(win_frame, text="찾아보기", command=self.browse_manifest_file)
        manifest_btn.grid(row=2, column=2, padx=5, pady=5)

        # 리소스 추가 프레임
        resource_frame = ttk.LabelFrame(scrollable_frame, text="리소스 추가 (--resource)")
        resource_frame.pack(fill=tk.X, padx=10, pady=5)

        self.resources = []
        self.resource_listbox = tk.Listbox(resource_frame, width=60, height=5)
        self.resource_listbox.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky=tk.W + tk.E)

        add_resource_btn = ttk.Button(resource_frame, text="리소스 추가", command=self.add_resource)
        add_resource_btn.grid(row=1, column=0, padx=5, pady=5)

        remove_resource_btn = ttk.Button(resource_frame, text="제거", command=self.remove_resource)
        remove_resource_btn.grid(row=1, column=1, padx=5, pady=5)

        # 버전 정보 프레임
        version_info_frame = ttk.LabelFrame(scrollable_frame, text="버전 정보")
        version_info_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(version_info_frame, text="파일 버전:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.file_version = tk.StringVar(value="1.0.0.0")
        ttk.Entry(version_info_frame, textvariable=self.file_version, width=20).grid(row=0, column=1, padx=5, pady=5,
                                                                                     sticky=tk.W)

        ttk.Label(version_info_frame, text="제품 버전:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.product_version = tk.StringVar(value="1.0.0.0")
        ttk.Entry(version_info_frame, textvariable=self.product_version, width=20).grid(row=0, column=3, padx=5, pady=5,
                                                                                        sticky=tk.W)

        ttk.Label(version_info_frame, text="회사명:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.company_name = tk.StringVar()
        ttk.Entry(version_info_frame, textvariable=self.company_name, width=20).grid(row=1, column=1, padx=5, pady=5,
                                                                                     sticky=tk.W)

        ttk.Label(version_info_frame, text="제품명:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        self.product_name = tk.StringVar()
        ttk.Entry(version_info_frame, textvariable=self.product_name, width=20).grid(row=1, column=3, padx=5, pady=5,
                                                                                     sticky=tk.W)

        # 버전 정보 생성 버튼
        generate_version_btn = ttk.Button(version_info_frame, text="버전 파일 생성", command=self.generate_version_file)
        generate_version_btn.grid(row=2, column=0, columnspan=4, padx=5, pady=5)

    def check_internet_connection(self):
        """인터넷 연결 상태 확인"""
        try:
            # Google에 ping 보내기
            process = subprocess.run(
                ["ping", "-n", "1", "google.com"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=5
            )
            return process.returncode == 0
        except Exception:
            return False

    def create_virtual_env_and_install_packages(self, packages):
        """가상환경 생성 및 패키지 설치"""
        try:
            # 임시 디렉토리 생성
            temp_dir = os.path.join(os.path.dirname(self.script_path.get()), "temp_venv")
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

            # 가상환경 생성
            self.log_text.insert(tk.END, f"가상환경 생성 중: {temp_dir}\n", "info")
            self.log_text.see(tk.END)
            self.root.update_idletasks()

            process = subprocess.run(
                [sys.executable, "-m", "venv", temp_dir],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            if process.returncode != 0:
                self.log_text.insert(tk.END, f"가상환경 생성 실패: {process.stderr}\n", "error")
                self.log_text.see(tk.END)
                self.root.update_idletasks()
                return None, []

            # 가상환경의 pip 경로
            pip_path = os.path.join(temp_dir, "Scripts", "pip.exe") if os.name == "nt" else os.path.join(temp_dir,
                                                                                                         "bin", "pip")
            python_path = os.path.join(temp_dir, "Scripts", "python.exe") if os.name == "nt" else os.path.join(temp_dir,
                                                                                                               "bin",
                                                                                                               "python")

            # 파이썬 기본 모듈 목록 (설치 시도에서 제외)
            standard_libs = [
                "os", "sys", "re", "json", "time", "datetime", "random", "math", "hashlib",
                "subprocess", "shutil", "glob", "argparse", "collections", "copy", "csv",
                "enum", "functools", "itertools", "io", "logging", "pickle", "platform",
                "string", "tempfile", "threading", "traceback", "types", "typing", "uuid",
                "warnings", "weakref", "zipfile"
            ]

            # pip 업그레이드 먼저 실행
            self.log_text.insert(tk.END, "pip 업그레이드 중...\n", "info")
            self.log_text.see(tk.END)
            self.root.update_idletasks()

            process = subprocess.run(
                [python_path, "-m", "pip", "install", "--upgrade", "pip"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            if process.returncode == 0:
                self.log_text.insert(tk.END, "pip 업그레이드 완료\n", "success")
            else:
                self.log_text.insert(tk.END, f"pip 업그레이드 실패: {process.stderr}\n", "warning")

            self.log_text.see(tk.END)
            self.root.update_idletasks()

            # pyinstaller 먼저 설치
            self.log_text.insert(tk.END, "PyInstaller 설치 중...\n", "info")
            self.log_text.see(tk.END)
            self.root.update_idletasks()

            process = subprocess.run(
                [pip_path, "install", "pyinstaller"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            if process.returncode == 0:
                self.log_text.insert(tk.END, "PyInstaller 설치 완료\n", "success")
            else:
                self.log_text.insert(tk.END, f"PyInstaller 설치 실패: {process.stderr}\n", "error")

            self.log_text.see(tk.END)
            self.root.update_idletasks()

            # tkinter는 tk로 설치
            if "tkinter" in packages:
                self.log_text.insert(tk.END, "tkinter(tk) 설치 중...\n", "info")
                self.log_text.see(tk.END)
                self.root.update_idletasks()

                process = subprocess.run(
                    [pip_path, "install", "tk"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )

                if process.returncode == 0:
                    self.log_text.insert(tk.END, "tkinter(tk) 설치 완료\n", "success")
                else:
                    self.log_text.insert(tk.END, f"tkinter(tk) 설치 실패: {process.stderr}\n", "warning")

                self.log_text.see(tk.END)
                self.root.update_idletasks()

            # 나머지 패키지 설치 (기본 모듈 제외)
            for package in packages:
                # 기본 모듈이거나 이미 설치한 패키지는 건너뛰기
                if package in standard_libs or package == "pyinstaller" or package == "tkinter":
                    continue

                self.log_text.insert(tk.END, f"패키지 설치 중: {package}\n", "info")
                self.log_text.see(tk.END)
                self.root.update_idletasks()

                process = subprocess.run(
                    [pip_path, "install", package],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )

                if process.returncode == 0:
                    self.log_text.insert(tk.END, f"패키지 설치 완료: {package}\n", "success")
                else:
                    self.log_text.insert(tk.END, f"패키지 설치 실패: {package} - {process.stderr}\n", "warning")

                self.log_text.see(tk.END)
                self.root.update_idletasks()

            # 설치된 패키지 목록 가져오기
            process = subprocess.run(
                [pip_path, "freeze"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            if process.returncode == 0:
                installed_packages = [line.split('==')[0] for line in process.stdout.splitlines() if line]
                self.log_text.insert(tk.END, f"설치된 패키지: {', '.join(installed_packages)}\n", "info")
                self.log_text.see(tk.END)
                self.root.update_idletasks()
                return temp_dir, installed_packages
            else:
                self.log_text.insert(tk.END, f"패키지 목록 가져오기 실패: {process.stderr}\n", "error")
                self.log_text.see(tk.END)
                self.root.update_idletasks()
                return temp_dir, []

        except Exception as e:
            self.log_text.insert(tk.END, f"가상환경 생성 중 오류 발생: {str(e)}\n", "error")
            self.log_text.see(tk.END)
            self.root.update_idletasks()
            return None, []

    def create_execution_tab(self):
        """실행 및 로그 탭 생성"""
        self.tab_execution = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_execution, text="실행 및 로그")

        # 명령어 프레임
        command_frame = ttk.LabelFrame(self.tab_execution, text="PyInstaller 명령어")
        command_frame.pack(fill=tk.X, padx=10, pady=5)

        self.command_text = scrolledtext.ScrolledText(command_frame, width=80, height=5)
        self.command_text.pack(fill=tk.X, padx=5, pady=5)

        # 버튼 프레임
        button_frame = ttk.Frame(self.tab_execution)
        button_frame.pack(fill=tk.X, padx=10, pady=5)

        generate_btn = ttk.Button(button_frame, text="명령어 생성", command=self.generate_command)
        generate_btn.pack(side=tk.LEFT, padx=5, pady=5)

        execute_btn = ttk.Button(button_frame, text="실행", command=self.execute_command)
        execute_btn.pack(side=tk.LEFT, padx=5, pady=5)

        save_btn = ttk.Button(button_frame, text="설정 저장", command=self.save_project)
        save_btn.pack(side=tk.LEFT, padx=5, pady=5)

        # 안전하게 모듈 추가하기 체크박스 추가
        self.safe_module_var = tk.BooleanVar(value=True)  # 기본값 True로 설정
        safe_module_check = ttk.Checkbutton(
            button_frame,
            text="안전하게 모듈 추가하기",
            variable=self.safe_module_var
        )
        safe_module_check.pack(side=tk.LEFT, padx=5, pady=5)

        # 진행 상황 프레임
        progress_frame = ttk.LabelFrame(self.tab_execution, text="진행 상황")
        progress_frame.pack(fill=tk.X, padx=10, pady=5)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, padx=5, pady=5)

        self.progress_label = ttk.Label(progress_frame, text="준비됨")
        self.progress_label.pack(anchor=tk.W, padx=5)

        # 로그 프레임
        log_frame = ttk.LabelFrame(self.tab_execution, text="로그")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.log_text = scrolledtext.ScrolledText(log_frame, width=80, height=15)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 로그 텍스트에 태그 설정
        self.log_text.tag_configure("error", foreground="red")
        self.log_text.tag_configure("warning", foreground="orange")
        self.log_text.tag_configure("info", foreground="blue")
        self.log_text.tag_configure("success", foreground="green")

        # 로그 버튼 프레임
        log_button_frame = ttk.Frame(log_frame)
        log_button_frame.pack(fill=tk.X, padx=5, pady=5)

        clear_log_btn = ttk.Button(log_button_frame, text="로그 지우기", command=self.clear_log)
        clear_log_btn.pack(side=tk.LEFT, padx=5)

        save_log_btn = ttk.Button(log_button_frame, text="로그 저장", command=self.save_log)
        save_log_btn.pack(side=tk.LEFT, padx=5)

        # 생성된 파일 확인하기 버튼 추가
        self.open_output_btn = ttk.Button(log_button_frame, text="생성된 파일 확인하기",
                                          command=self.open_output_folder, state="disabled")
        self.open_output_btn.pack(side=tk.LEFT, padx=5)

    def open_output_folder(self):
        """생성된 출력 폴더 열기"""
        try:
            output_path = self.output_dir.get() if self.output_dir.get() else "./dist"
            app_name = self.app_name.get() if self.app_name.get() else \
            os.path.splitext(os.path.basename(self.script_path.get()))[0]

            # 빌드 타입에 따라 경로 결정
            if self.build_type.get() == "--onefile":
                folder_path = output_path
            else:
                folder_path = os.path.join(output_path, app_name)

            # 폴더가 존재하는지 확인
            if os.path.exists(folder_path):
                # Windows에서 폴더 열기
                os.startfile(folder_path)
            else:
                messagebox.showwarning("경고", "출력 폴더를 찾을 수 없습니다.")
        except Exception as e:
            messagebox.showerror("오류", f"폴더를 열 수 없습니다: {str(e)}")

    def analyze_and_add_imports(self, file_path):
        """파일을 분석하고 숨겨진 임포트를 자동으로 추가"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)
            imports = set()

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        imports.add(name.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module.split('.')[0])

            # 기존 숨겨진 임포트 목록 초기화
            self.hidden_imports = []
            self.hidden_listbox.delete(0, tk.END)

            # 분석된 임포트 추가
            for imp in sorted(imports):
                self.hidden_imports.append(imp)
                self.hidden_listbox.insert(tk.END, imp)

            # 로그에 분석 결과 표시
            self.log_text.delete("1.0", tk.END)
            self.log_text.insert(tk.END, "=== 임포트 분석 결과 ===\n", "info")
            for imp in sorted(imports):
                self.log_text.insert(tk.END, f"- {imp}\n")
            self.log_text.insert(tk.END, "=======================\n", "info")
            self.log_text.see(tk.END)

            # 상태 업데이트
            self.status_bar.config(text=f"파일 분석 완료: {len(imports)}개의 임포트를 찾았습니다.")

        except Exception as e:
            messagebox.showerror("오류", f"파일 분석 중 오류 발생: {str(e)}")

    # 유틸리티 메서드
    def browse_script(self):
        """Python 스크립트 파일 선택"""
        file_path = filedialog.askopenfilename(
            title="Python 스크립트 선택",
            filetypes=[("Python 파일", "*.py"), ("모든 파일", "*.*")]
        )
        if file_path:
            self.script_path.set(file_path)
            # 파일 이름을 기반으로 앱 이름 설정
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            self.app_name.set(base_name)

            # 파일 분석 및 임포트 추가
            self.analyze_and_add_imports(file_path)

    def browse_output_dir(self):
        """출력 디렉토리 선택"""
        dir_path = filedialog.askdirectory(title="출력 폴더 선택")
        if dir_path:
            self.output_dir.set(dir_path)

    def browse_work_dir(self):
        """작업 디렉토리 선택"""
        dir_path = filedialog.askdirectory(title="작업 폴더 선택")
        if dir_path:
            self.work_dir.set(dir_path)

    def browse_upx_dir(self):
        """UPX 디렉토리 선택"""
        dir_path = filedialog.askdirectory(title="UPX 폴더 선택")
        if dir_path:
            self.upx_dir.set(dir_path)

    def browse_icon(self):
        """아이콘 파일 선택"""
        file_path = filedialog.askopenfilename(
            title="아이콘 파일 선택",
            filetypes=[("아이콘 파일", "*.ico"), ("모든 파일", "*.*")]
        )
        if file_path:
            self.icon_file.set(file_path)

    def browse_version_file(self):
        """버전 파일 선택"""
        file_path = filedialog.askopenfilename(
            title="버전 파일 선택",
            filetypes=[("텍스트 파일", "*.txt"), ("모든 파일", "*.*")]
        )
        if file_path:
            self.version_file.set(file_path)

    def browse_manifest_file(self):
        """매니페스트 파일 선택"""
        file_path = filedialog.askopenfilename(
            title="매니페스트 파일 선택",
            filetypes=[("XML 파일", "*.xml"), ("모든 파일", "*.*")]
        )
        if file_path:
            self.manifest_file.set(file_path)

    def add_data_file(self):
        """데이터 파일 추가"""
        file_path = filedialog.askopenfilename(title="데이터 파일 선택")
        if file_path:
            dest_dir = filedialog.askdirectory(title="대상 디렉토리 선택 (상대 경로)")
            if not dest_dir:
                dest_dir = "."

            # Windows 경로 구분자 처리
            entry = f"{file_path};{dest_dir}"
            self.data_files.append(entry)
            self.data_listbox.insert(tk.END, entry)

    def remove_data_file(self):
        """선택된 데이터 파일 제거"""
        selected = self.data_listbox.curselection()
        if selected:
            index = selected[0]
            self.data_listbox.delete(index)
            self.data_files.pop(index)

    def add_binary_file(self):
        """바이너리 파일 추가"""
        file_path = filedialog.askopenfilename(title="바이너리 파일 선택")
        if file_path:
            dest_dir = filedialog.askdirectory(title="대상 디렉토리 선택 (상대 경로)")
            if not dest_dir:
                dest_dir = "."

            # Windows 경로 구분자 처리
            entry = f"{file_path};{dest_dir}"
            self.binary_files.append(entry)
            self.binary_listbox.insert(tk.END, entry)

    def remove_binary_file(self):
        """선택된 바이너리 파일 제거"""
        selected = self.binary_listbox.curselection()
        if selected:
            index = selected[0]
            self.binary_listbox.delete(index)
            self.binary_files.pop(index)

    def add_hidden_import(self):
        """숨겨진 임포트 추가"""
        module_name = self.hidden_import_entry.get().strip()
        if module_name:
            self.hidden_imports.append(module_name)
            self.hidden_listbox.insert(tk.END, module_name)
            self.hidden_import_entry.delete(0, tk.END)

    def remove_hidden_import(self):
        """선택된 숨겨진 임포트 제거"""
        selected = self.hidden_listbox.curselection()
        if selected:
            index = selected[0]
            self.hidden_listbox.delete(index)
            self.hidden_imports.pop(index)

    def add_exclude_module(self):
        """제외할 모듈 추가"""
        module_name = self.exclude_module_entry.get().strip()
        if module_name:
            self.exclude_modules.append(module_name)
            self.exclude_listbox.insert(tk.END, module_name)
            self.exclude_module_entry.delete(0, tk.END)

    def remove_exclude_module(self):
        """선택된 제외 모듈 제거"""
        selected = self.exclude_listbox.curselection()
        if selected:
            index = selected[0]
            self.exclude_listbox.delete(index)
            self.exclude_modules.pop(index)

    def add_hooks_dir(self):
        """훅 디렉토리 추가"""
        dir_path = filedialog.askdirectory(title="훅 디렉토리 선택")
        if dir_path:
            self.hooks_dirs.append(dir_path)
            self.hooks_dir_listbox.insert(tk.END, dir_path)

    def remove_hooks_dir(self):
        """선택된 훅 디렉토리 제거"""
        selected = self.hooks_dir_listbox.curselection()
        if selected:
            index = selected[0]
            self.hooks_dir_listbox.delete(index)
            self.hooks_dirs.pop(index)

    def add_runtime_hook(self):
        """런타임 훅 추가"""
        file_path = filedialog.askopenfilename(
            title="런타임 훅 파일 선택",
            filetypes=[("Python 파일", "*.py"), ("모든 파일", "*.*")]
        )
        if file_path:
            self.runtime_hooks.append(file_path)
            self.runtime_hook_listbox.insert(tk.END, file_path)

    def remove_runtime_hook(self):
        """선택된 런타임 훅 제거"""
        selected = self.runtime_hook_listbox.curselection()
        if selected:
            index = selected[0]
            self.runtime_hook_listbox.delete(index)
            self.runtime_hooks.pop(index)

    def add_resource(self):
        """리소스 추가"""
        file_path = filedialog.askopenfilename(title="리소스 파일 선택")
        if file_path:
            # 리소스 타입과 이름 입력 대화상자
            resource_dialog = tk.Toplevel(self.root)
            resource_dialog.title("리소스 정보")
            resource_dialog.geometry("300x150")
            resource_dialog.transient(self.root)
            resource_dialog.grab_set()

            ttk.Label(resource_dialog, text="리소스 타입 (선택사항):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
            resource_type = ttk.Entry(resource_dialog, width=20)
            resource_type.grid(row=0, column=1, padx=5, pady=5)

            ttk.Label(resource_dialog, text="리소스 이름 (선택사항):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
            resource_name = ttk.Entry(resource_dialog, width=20)
            resource_name.grid(row=1, column=1, padx=5, pady=5)

            ttk.Label(resource_dialog, text="언어 (선택사항):").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
            resource_lang = ttk.Entry(resource_dialog, width=20)
            resource_lang.grid(row=2, column=1, padx=5, pady=5)

            def on_ok():
                type_val = resource_type.get().strip()
                name_val = resource_name.get().strip()
                lang_val = resource_lang.get().strip()

                resource_str = file_path
                if type_val:
                    resource_str += f",{type_val}"
                    if name_val:
                        resource_str += f",{name_val}"
                        if lang_val:
                            resource_str += f",{lang_val}"

                self.resources.append(resource_str)
                self.resource_listbox.insert(tk.END, resource_str)
                resource_dialog.destroy()

            ttk.Button(resource_dialog, text="확인", command=on_ok).grid(row=3, column=0, columnspan=2, padx=5, pady=10)

            # 대화상자가 닫힐 때까지 대기
            self.root.wait_window(resource_dialog)

    def remove_resource(self):
        """선택된 리소스 제거"""
        selected = self.resource_listbox.curselection()
        if selected:
            index = selected[0]
            self.resource_listbox.delete(index)
            self.resources.pop(index)

    def generate_version_file(self):
        """버전 정보 파일 생성"""
        file_path = filedialog.asksaveasfilename(
            title="버전 파일 저장",
            defaultextension=".txt",
            filetypes=[("텍스트 파일", "*.txt"), ("모든 파일", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write("# UTF-8\n")
                    f.write("#\n")
                    f.write("# For more details about fixed file info 'ffi' see:\n")
                    f.write("# http://msdn.microsoft.com/en-us/library/ms646997.aspx\n")
                    f.write("VSVersionInfo(\n")
                    f.write("  ffi=FixedFileInfo(\n")
                    f.write(f"    # filevers and prodvers should be always a tuple with four items: (1, 2, 3, 4)\n")

                    # 버전 문자열을 튜플로 변환
                    file_ver = self.file_version.get().split('.')
                    file_ver = tuple(int(v) for v in file_ver) if len(file_ver) == 4 else (1, 0, 0, 0)

                    prod_ver = self.product_version.get().split('.')
                    prod_ver = tuple(int(v) for v in prod_ver) if len(prod_ver) == 4 else (1, 0, 0, 0)

                    f.write(f"    filevers={file_ver},\n")
                    f.write(f"    prodvers={prod_ver},\n")
                    f.write("    # Contains a bitmask that specifies the valid bits 'flags'\n")
                    f.write("    mask=0x3f,\n")
                    f.write("    # Contains a bitmask that specifies the Boolean attributes of the file.\n")
                    f.write("    flags=0x0,\n")
                    f.write("    # The operating system for which this file was designed.\n")
                    f.write("    # 0x4 - NT and there is no need to change it.\n")
                    f.write("    OS=0x40004,\n")
                    f.write("    # The general type of file.\n")
                    f.write("    # 0x1 - the file is an application.\n")
                    f.write("    fileType=0x1,\n")
                    f.write("    # The function of the file.\n")
                    f.write("    # 0x0 - the function is not defined for this fileType\n")
                    f.write("    subtype=0x0,\n")
                    f.write("    # Creation date and time stamp.\n")
                    f.write("    date=(0, 0)\n")
                    f.write("    ),\n")
                    f.write("  kids=[\n")
                    f.write("    StringFileInfo(\n")
                    f.write("      [\n")
                    f.write("      StringTable(\n")
                    f.write("        u'040904B0',\n")
                    f.write("        [StringStruct(u'CompanyName', u'%s'),\n" % self.company_name.get())
                    f.write("        StringStruct(u'FileDescription', u'%s'),\n" % self.app_name.get())
                    f.write("        StringStruct(u'FileVersion', u'%s'),\n" % self.file_version.get())
                    f.write("        StringStruct(u'InternalName', u'%s'),\n" % self.app_name.get())
                    f.write("        StringStruct(u'LegalCopyright', u'Copyright © %s'),\n" % datetime.now().year)
                    f.write("        StringStruct(u'OriginalFilename', u'%s.exe'),\n" % self.app_name.get())
                    f.write("        StringStruct(u'ProductName', u'%s'),\n" % self.product_name.get())
                    f.write("        StringStruct(u'ProductVersion', u'%s')]\n" % self.product_version.get())
                    f.write("      )\n")
                    f.write("      ]),\n")
                    f.write("    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])\n")
                    f.write("  ]\n")
                    f.write(")\n")

                self.version_file.set(file_path)
                messagebox.showinfo("성공", "버전 파일이 생성되었습니다.")
            except Exception as e:
                messagebox.showerror("오류", f"버전 파일 생성 중 오류 발생: {str(e)}")

    def analyze_imports(self):
        """Python 파일의 임포트 분석"""
        file_path = self.script_path.get()
        if not file_path or not os.path.isfile(file_path):
            messagebox.showwarning("경고", "유효한 Python 파일을 선택해주세요.")
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)
            imports = set()

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        imports.add(name.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module.split('.')[0])

            # 결과 표시
            self.log_text.insert(tk.END, "=== 임포트 분석 결과 ===\n", "info")
            for imp in sorted(imports):
                self.log_text.insert(tk.END, f"- {imp}\n")
            self.log_text.insert(tk.END, "=======================\n", "info")
            self.log_text.see(tk.END)

            # 사용자에게 추가할지 물어보기
            if messagebox.askyesno("임포트 추가", "분석된 임포트를 숨겨진 임포트 목록에 추가하시겠습니까?"):
                for imp in imports:
                    if imp not in self.hidden_imports:
                        self.hidden_imports.append(imp)
                        self.hidden_listbox.insert(tk.END, imp)

        except Exception as e:
            messagebox.showerror("오류", f"파일 분석 중 오류 발생: {str(e)}")

    def generate_command(self):
        """PyInstaller 명령어 생성"""
        script_path = self.script_path.get()
        if not script_path:
            messagebox.showwarning("경고", "Python 파일을 선택해주세요.")
            return

        # 안전하게 모듈 추가하기 옵션이 켜져 있고 인터넷 연결이 되어 있는 경우
        if self.safe_module_var.get() and self.check_internet_connection():
            self.log_text.insert(tk.END, "인터넷 연결 확인됨. 안전 모드로 모듈 추가를 시작합니다.\n", "info")
            self.log_text.see(tk.END)
            self.root.update_idletasks()

            # 파일 분석하여 필요한 패키지 목록 가져오기
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)
            imports = set()

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        imports.add(name.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module.split('.')[0])

            # 필요한 패키지 목록 생성 (pyinstaller는 자동으로 추가됨)
            required_packages = list(imports)

            # 가상환경 생성 및 패키지 설치
            venv_dir, installed_packages = self.create_virtual_env_and_install_packages(required_packages)

            if venv_dir and installed_packages:
                self.log_text.insert(tk.END, "가상환경 생성 및 패키지 설치 완료. PyInstaller 명령어가 생성되었습니다. 실행버튼을 눌러주세요\n", "info")
                self.log_text.see(tk.END)
                self.root.update_idletasks()

                # 기존 숨겨진 임포트 목록 초기화 및 설치된 패키지로 업데이트
                self.hidden_imports = installed_packages
                self.hidden_listbox.delete(0, tk.END)
                for package in installed_packages:
                    self.hidden_listbox.insert(tk.END, package)
        else:
            if self.safe_module_var.get():
                self.log_text.insert(tk.END, "인터넷 연결이 확인되지 않아 기존 방식으로 진행합니다.\n", "warning")
                self.log_text.see(tk.END)
                self.root.update_idletasks()

        # 기본 명령어
        command = ["pyinstaller"]

        # 기본 옵션
        if self.build_type.get():
            command.append(self.build_type.get())

        if self.console_option.get():
            command.append(self.console_option.get())

        # 이름 옵션
        if self.app_name.get():
            command.append(f"--name=\"{self.app_name.get()}\"")

        # 출력 디렉토리
        if self.output_dir.get():
            command.append(f"--distpath=\"{self.output_dir.get()}\"")

        # 작업 디렉토리
        if self.work_dir.get():
            command.append(f"--workpath=\"{self.work_dir.get()}\"")

        # 일반 옵션
        if self.clean_build.get():
            command.append("--clean")

        if self.no_confirm.get():
            command.append("--noconfirm")

        if self.log_level.get() != "INFO":
            command.append(f"--log-level={self.log_level.get()}")

        # UPX 옵션
        if not self.use_upx.get() or self.noupx.get():
            command.append("--noupx")
        elif self.upx_dir.get():
            command.append(f"--upx-dir=\"{self.upx_dir.get()}\"")

        # 고급 옵션
        if self.strip.get():
            command.append("--strip")

        if self.ascii.get():
            command.append("--ascii")

        if self.uac_admin.get():
            command.append("--uac-admin")

        if self.uac_uiaccess.get():
            command.append("--uac-uiaccess")

        if self.win_private_assemblies.get():
            command.append("--win-private-assemblies")

        if self.win_no_prefer_redirects.get():
            command.append("--win-no-prefer-redirects")

        # 데이터 파일
        for data_file in self.data_files:
            command.append(f"--add-data=\"{data_file}\"")

        # 바이너리 파일
        for binary_file in self.binary_files:
            command.append(f"--add-binary=\"{binary_file}\"")

        # 숨겨진 임포트
        for hidden_import in self.hidden_imports:
            command.append(f"--hidden-import={hidden_import}")

        # 제외 모듈
        for exclude_module in self.exclude_modules:
            command.append(f"--exclude-module={exclude_module}")

        # 훅 디렉토리
        for hooks_dir in self.hooks_dirs:
            command.append(f"--additional-hooks-dir=\"{hooks_dir}\"")

        # 런타임 훅
        for runtime_hook in self.runtime_hooks:
            command.append(f"--runtime-hook=\"{runtime_hook}\"")

        # 플랫폼 특화 옵션
        if self.icon_file.get():
            command.append(f"--icon=\"{self.icon_file.get()}\"")

        if self.version_file.get():
            command.append(f"--version-file=\"{self.version_file.get()}\"")

        if self.manifest_file.get():
            command.append(f"--manifest=\"{self.manifest_file.get()}\"")

        # 리소스
        for resource in self.resources:
            command.append(f"--resource=\"{resource}\"")

        # 복잡한 패키지에 대한 collect-all 옵션 추가
        if "pandas" in self.hidden_imports:
            command.append("--collect-all=pandas")
        if "numpy" in self.hidden_imports:
            command.append("--collect-all=numpy")

        # 스크립트 경로 추가
        command.append(f"\"{script_path}\"")

        # 명령어 표시
        final_command = " ".join(command)
        self.command_text.delete("1.0", tk.END)
        self.command_text.insert(tk.END, final_command)

        # 상태 업데이트
        self.status_bar.config(text="명령어가 생성되었습니다.")

    def show_build_results(self):
        """빌드 결과 정보 표시"""
        try:
            output_path = self.output_dir.get() if self.output_dir.get() else "./dist"
            app_name = self.app_name.get() if self.app_name.get() else \
            os.path.splitext(os.path.basename(self.script_path.get()))[0]

            if self.build_type.get() == "--onefile":
                exe_path = os.path.join(output_path, f"{app_name}.exe")
                if os.path.exists(exe_path):
                    size_mb = os.path.getsize(exe_path) / (1024 * 1024)
                    self.log_text.insert(tk.END, f"\n빌드 결과:\n", "info")
                    self.log_text.insert(tk.END, f"- 실행 파일: {exe_path}\n")
                    self.log_text.insert(tk.END, f"- 파일 크기: {size_mb:.2f} MB\n")
                    self.log_text.insert(tk.END,
                                         f"- 생성 시간: {datetime.fromtimestamp(os.path.getctime(exe_path)).strftime('%Y-%m-%d %H:%M:%S')}\n")
            else:
                dir_path = os.path.join(output_path, app_name)
                if os.path.exists(dir_path):
                    exe_path = os.path.join(dir_path, f"{app_name}.exe")
                    if os.path.exists(exe_path):
                        size_mb = os.path.getsize(exe_path) / (1024 * 1024)
                        total_size = 0
                        file_count = 0

                        for root, dirs, files in os.walk(dir_path):
                            for file in files:
                                file_path = os.path.join(root, file)
                                total_size += os.path.getsize(file_path)
                                file_count += 1

                        total_size_mb = total_size / (1024 * 1024)

                        self.log_text.insert(tk.END, f"\n빌드 결과:\n", "info")
                        self.log_text.insert(tk.END, f"- 출력 디렉토리: {dir_path}\n")
                        self.log_text.insert(tk.END, f"- 실행 파일: {exe_path}\n")
                        self.log_text.insert(tk.END, f"- 실행 파일 크기: {size_mb:.2f} MB\n")
                        self.log_text.insert(tk.END, f"- 총 파일 수: {file_count}개\n")
                        self.log_text.insert(tk.END, f"- 총 크기: {total_size_mb:.2f} MB\n")
        except Exception as e:
            self.log_text.insert(tk.END, f"빌드 정보 수집 중 오류 발생: {str(e)}\n", "error")

    def execute_command(self):
        """PyInstaller 명령어 실행"""
        command = self.command_text.get("1.0", tk.END).strip()
        if not command:
            messagebox.showwarning("경고", "실행할 명령어가 없습니다. 먼저 명령어를 생성해주세요.")
            return

        # 로그 초기화
        self.clear_log()

        # 로그 초기화
        self.clear_log()

        # 진행 상황 초기화
        self.progress_var.set(0)
        self.progress_label.config(text="빌드 시작...")

        # 파일 확인 버튼 비활성화
        self.open_output_btn.config(state="disabled")

        # 시작 시간 기록 및 로그에 표시
        start_time = datetime.now()
        self.log_text.insert(tk.END, f"[{start_time.strftime('%H:%M:%S')}] 빌드 시작...\n", "info")
        self.log_text.see(tk.END)

        # 명령어 실행 스레드
        def run_command():
            try:
                # 프로세스 실행 - 버퍼링 없이 실시간 출력을 위한 설정
                process = subprocess.Popen(
                    command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    encoding='CP949',  # 명시적으로 UTF-8 인코딩 지정
                    errors='replace',  # 디코딩할 수 없는 바이트는 대체 문자로 대체
                    text=True,
                    bufsize=1,  # 라인 버퍼링
                    universal_newlines=True
                )

                # 진행 상태 추적을 위한 키워드
                progress_keywords = {
                    "Determining": 5,
                    "Analyzing": 10,
                    "Processing": 30,
                    "Checking": 50,
                    "Building": 70,
                    "Building EXE": 80,
                    "Copying": 90,
                    "Completed": 100
                }

                # 표준 출력 처리 함수
                def read_output(pipe, is_error=False):
                    for line in iter(pipe.readline, ''):
                        timestamp = datetime.now().strftime('%H:%M:%S')

                        # GUI 업데이트는 메인 스레드에서 해야 함
                        if is_error and "ERROR" in line:
                            self.root.after(0, lambda l=line, t=timestamp: (
                                self.log_text.insert(tk.END, f"[{t}] {l}", "error"),
                                self.log_text.see(tk.END)
                            ))
                        elif is_error and "WARNING" in line:
                            self.root.after(0, lambda l=line, t=timestamp: (
                                self.log_text.insert(tk.END, f"[{t}] {l}", "warning"),
                                self.log_text.see(tk.END)
                            ))
                        else:
                            self.root.after(0, lambda l=line, t=timestamp: (
                                self.log_text.insert(tk.END, f"[{t}] {l}"),
                                self.log_text.see(tk.END)
                            ))

                        # 진행 상태 업데이트
                        for keyword, progress in progress_keywords.items():
                            if keyword in line:
                                self.root.after(0, lambda p=progress: self.progress_var.set(p))
                                self.root.after(0, lambda l=line: self.progress_label.config(text=l.strip()))
                                break

                        # 실시간 업데이트를 위해 잠시 대기
                        time.sleep(0.01)

                # 출력 및 에러 스트림을 별도 스레드에서 읽기
                stdout_thread = threading.Thread(target=read_output, args=(process.stdout, False))
                stderr_thread = threading.Thread(target=read_output, args=(process.stderr, True))

                stdout_thread.daemon = True
                stderr_thread.daemon = True

                stdout_thread.start()
                stderr_thread.start()

                # 프로세스 완료 대기
                process.wait()

                # 스레드 완료 대기
                stdout_thread.join()
                stderr_thread.join()

                # 종료 시간 기록
                end_time = datetime.now()
                duration = end_time - start_time

                if process.returncode == 0:
                    self.root.after(0, lambda: self.progress_var.set(100))
                    self.root.after(0, lambda: self.progress_label.config(text="빌드 완료!"))
                    self.root.after(0, lambda: self.log_text.insert(tk.END,
                                                                    f"[{end_time.strftime('%H:%M:%S')}] 빌드 완료! (소요 시간: {duration.seconds}초)\n",
                                                                    "success"))

                    # 빌드 결과 정보 표시
                    self.root.after(0, lambda: self.show_build_results())

                    # 파일 확인 버튼 활성화
                    self.root.after(0, lambda: self.open_output_btn.config(state="normal"))

                    # 완료 메시지 표시
                    self.root.after(0, lambda: messagebox.showinfo("빌드 완료", "PyInstaller 빌드가 성공적으로 완료되었습니다."))
                else:
                    self.root.after(0, lambda: self.progress_label.config(text="빌드 실패!"))
                    self.root.after(0, lambda: self.log_text.insert(tk.END,
                                                                    f"[{end_time.strftime('%H:%M:%S')}] 빌드 실패! (소요 시간: {duration.seconds}초)\n",
                                                                    "error"))
                    self.root.after(0,
                                    lambda: messagebox.showerror("빌드 실패", "PyInstaller 빌드 중 오류가 발생했습니다. 로그를 확인해주세요."))

            except Exception as e:
                self.root.after(0, lambda: self.log_text.insert(tk.END, f"명령어 실행 중 오류 발생: {str(e)}\n", "error"))
                self.root.after(0, lambda: self.progress_label.config(text="오류 발생!"))
                self.root.after(0, lambda: messagebox.showerror("오류", f"명령어 실행 중 오류가 발생했습니다: {str(e)}"))

            finally:
                # 상태 업데이트
                self.root.after(0, lambda: self.status_bar.config(text="명령어 실행 완료"))

        # 스레드 시작
        threading.Thread(target=run_command, daemon=True).start()

        # 상태 업데이트
        self.status_bar.config(text="명령어 실행 중...")

    def clear_log(self):
        """로그 내용 지우기"""
        self.log_text.delete("1.0", tk.END)

    def save_log(self):
        """로그 내용 파일로 저장"""
        log_content = self.log_text.get("1.0", tk.END)
        if not log_content.strip():
            messagebox.showinfo("알림", "저장할 로그 내용이 없습니다.")
            return

        file_path = filedialog.asksaveasfilename(
            title="로그 저장",
            defaultextension=".log",
            filetypes=[("로그 파일", "*.log"), ("텍스트 파일", "*.txt"), ("모든 파일", "*.*")]
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(log_content)
                messagebox.showinfo("성공", "로그가 저장되었습니다.")
            except Exception as e:
                messagebox.showerror("오류", f"로그 저장 중 오류 발생: {str(e)}")

    def save_project(self):
        """현재 설정을 프로젝트 파일로 저장"""
        file_path = filedialog.asksaveasfilename(
            title="프로젝트 저장",
            defaultextension=".pyinstaller",
            filetypes=[("PyInstaller 프로젝트", "*.pyinstaller"), ("JSON 파일", "*.json"), ("모든 파일", "*.*")]
        )

        if file_path:
            try:
                project_data = {
                    "script_path": self.script_path.get(),
                    "app_name": self.app_name.get(),
                    "output_dir": self.output_dir.get(),
                    "work_dir": self.work_dir.get(),
                    "build_type": self.build_type.get(),
                    "console_option": self.console_option.get(),
                    "clean_build": self.clean_build.get(),
                    "no_confirm": self.no_confirm.get(),
                    "log_level": self.log_level.get(),
                    "use_upx": self.use_upx.get(),
                    "upx_dir": self.upx_dir.get(),
                    "noupx": self.noupx.get(),
                    "strip": self.strip.get(),
                    "ascii": self.ascii.get(),
                    "uac_admin": self.uac_admin.get(),
                    "uac_uiaccess": self.uac_uiaccess.get(),
                    "win_private_assemblies": self.win_private_assemblies.get(),
                    "win_no_prefer_redirects": self.win_no_prefer_redirects.get(),
                    "data_files": self.data_files,
                    "binary_files": self.binary_files,
                    "hidden_imports": self.hidden_imports,
                    "exclude_modules": self.exclude_modules,
                    "hooks_dirs": self.hooks_dirs,
                    "runtime_hooks": self.runtime_hooks,
                    "icon_file": self.icon_file.get(),
                    "version_file": self.version_file.get(),
                    "manifest_file": self.manifest_file.get(),
                    "resources": self.resources,
                    "file_version": self.file_version.get(),
                    "product_version": self.product_version.get(),
                    "company_name": self.company_name.get(),
                    "product_name": self.product_name.get()
                }

                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(project_data, f, indent=2, ensure_ascii=False)

                # 최근 프로젝트에 추가
                if file_path not in self.recent_projects:
                    self.recent_projects.insert(0, file_path)
                    if len(self.recent_projects) > 10:  # 최대 10개 유지
                        self.recent_projects.pop()
                    self.update_recent_projects_combo()

                # 설정 저장
                self.save_config()

                messagebox.showinfo("성공", "프로젝트가 저장되었습니다.")
            except Exception as e:
                messagebox.showerror("오류", f"프로젝트 저장 중 오류 발생: {str(e)}")

    def load_recent_project(self):
        """최근 프로젝트 불러오기"""
        selected_project = self.recent_combo.get()
        if selected_project and os.path.exists(selected_project):
            self.load_project_from_file(selected_project)
        else:
            messagebox.showwarning("경고", "유효한 프로젝트 파일을 선택해주세요.")

    def load_project_from_file(self, file_path):
        """파일에서 프로젝트 설정 불러오기"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                project_data = json.load(f)

            # 기본 설정 불러오기
            if "script_path" in project_data:
                self.script_path.set(project_data["script_path"])

            if "app_name" in project_data:
                self.app_name.set(project_data["app_name"])

            if "output_dir" in project_data:
                self.output_dir.set(project_data["output_dir"])

            if "work_dir" in project_data:
                self.work_dir.set(project_data["work_dir"])

            if "build_type" in project_data:
                self.build_type.set(project_data["build_type"])

            if "console_option" in project_data:
                self.console_option.set(project_data["console_option"])

            if "clean_build" in project_data:
                self.clean_build.set(project_data["clean_build"])

            if "no_confirm" in project_data:
                self.no_confirm.set(project_data["no_confirm"])

            if "log_level" in project_data:
                self.log_level.set(project_data["log_level"])

            # UPX 설정 불러오기
            if "use_upx" in project_data:
                self.use_upx.set(project_data["use_upx"])

            if "upx_dir" in project_data:
                self.upx_dir.set(project_data["upx_dir"])

            if "noupx" in project_data:
                self.noupx.set(project_data["noupx"])

            # 고급 옵션 불러오기
            if "strip" in project_data:
                self.strip.set(project_data["strip"])

            if "ascii" in project_data:
                self.ascii.set(project_data["ascii"])

            if "uac_admin" in project_data:
                self.uac_admin.set(project_data["uac_admin"])

            if "uac_uiaccess" in project_data:
                self.uac_uiaccess.set(project_data["uac_uiaccess"])

            if "win_private_assemblies" in project_data:
                self.win_private_assemblies.set(project_data["win_private_assemblies"])

            if "win_no_prefer_redirects" in project_data:
                self.win_no_prefer_redirects.set(project_data["win_no_prefer_redirects"])

            # 데이터 파일 불러오기
            if "data_files" in project_data:
                self.data_files = project_data["data_files"]
                self.data_listbox.delete(0, tk.END)
                for data_file in self.data_files:
                    self.data_listbox.insert(tk.END, data_file)

            # 바이너리 파일 불러오기
            if "binary_files" in project_data:
                self.binary_files = project_data["binary_files"]
                self.binary_listbox.delete(0, tk.END)
                for binary_file in self.binary_files:
                    self.binary_listbox.insert(tk.END, binary_file)

            # 숨겨진 임포트 불러오기
            if "hidden_imports" in project_data:
                self.hidden_imports = project_data["hidden_imports"]
                self.hidden_listbox.delete(0, tk.END)
                for hidden_import in self.hidden_imports:
                    self.hidden_listbox.insert(tk.END, hidden_import)

            # 제외 모듈 불러오기
            if "exclude_modules" in project_data:
                self.exclude_modules = project_data["exclude_modules"]
                self.exclude_listbox.delete(0, tk.END)
                for exclude_module in self.exclude_modules:
                    self.exclude_listbox.insert(tk.END, exclude_module)

            # 훅 디렉토리 불러오기
            if "hooks_dirs" in project_data:
                self.hooks_dirs = project_data["hooks_dirs"]
                self.hooks_dir_listbox.delete(0, tk.END)
                for hooks_dir in self.hooks_dirs:
                    self.hooks_dir_listbox.insert(tk.END, hooks_dir)

            # 런타임 훅 불러오기
            if "runtime_hooks" in project_data:
                self.runtime_hooks = project_data["runtime_hooks"]
                self.runtime_hook_listbox.delete(0, tk.END)
                for runtime_hook in self.runtime_hooks:
                    self.runtime_hook_listbox.insert(tk.END, runtime_hook)

            # 플랫폼 특화 옵션 불러오기
            if "icon_file" in project_data:
                self.icon_file.set(project_data["icon_file"])

            if "version_file" in project_data:
                self.version_file.set(project_data["version_file"])

            if "manifest_file" in project_data:
                self.manifest_file.set(project_data["manifest_file"])

            # 리소스 불러오기
            if "resources" in project_data:
                self.resources = project_data["resources"]
                self.resource_listbox.delete(0, tk.END)
                for resource in self.resources:
                    self.resource_listbox.insert(tk.END, resource)

            # 버전 정보 불러오기
            if "file_version" in project_data:
                self.file_version.set(project_data["file_version"])

            if "product_version" in project_data:
                self.product_version.set(project_data["product_version"])

            if "company_name" in project_data:
                self.company_name.set(project_data["company_name"])

            if "product_name" in project_data:
                self.product_name.set(project_data["product_name"])

            # 최근 프로젝트에 추가
            if file_path not in self.recent_projects:
                self.recent_projects.insert(0, file_path)
                if len(self.recent_projects) > 10:  # 최대 10개 유지
                    self.recent_projects.pop()
                self.update_recent_projects_combo()

            # 설정 저장
            self.save_config()

            # 명령어 생성
            self.generate_command()

            messagebox.showinfo("성공", "프로젝트를 불러왔습니다.")
        except Exception as e:
            messagebox.showerror("오류", f"프로젝트 불러오기 중 오류 발생: {str(e)}")

    def update_recent_projects_combo(self):
        """최근 프로젝트 콤보박스 업데이트"""
        self.recent_combo['values'] = self.recent_projects
        if self.recent_projects:
            self.recent_combo.current(0)

    def save_config(self):
        """설정 저장"""
        config_data = {
            "recent_projects": self.recent_projects
        }

        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"설정 저장 중 오류 발생: {str(e)}")

    def load_config(self):
        """설정 불러오기"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)

                if "recent_projects" in config_data:
                    self.recent_projects = config_data["recent_projects"]
                    # 존재하는 파일만 필터링
                    self.recent_projects = [p for p in self.recent_projects if os.path.exists(p)]
                    self.update_recent_projects_combo()
            except Exception as e:
                print(f"설정 불러오기 중 오류 발생: {str(e)}")


def main():
    root = tk.Tk()
    app = PyInstallerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
