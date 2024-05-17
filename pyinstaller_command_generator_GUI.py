import os
import tkinter as tk
import ast
from tkinter import messagebox
import subprocess
import threading

def generate_command():
    file_path = entry_path.get().replace("'", "").replace('"', "")
    one_file = get_checkbox_value()
    console = get_checkbox_value2()
    hidden_import = entry_hidden.get()

    if len(file_path) < 3:
        messagebox.showinfo(title="알림", message="py 파일을 찾을 수 없습니다. 경로를 확인해주십시오")
        command = "py 파일을 찾을 수 없습니다. 경로를 확인해주십시오"
        output_text.delete("1.0", tk.END)
        output_text.insert(tk.END, command)
    else:
        command = "pyinstaller"
        command += f" {file_path}"
        if one_file:
            command += f" {one_file}"
        if console:
            command += f" {console}"

        if hidden_import:
            hidden_import_list = hidden_import.split(",")
            for imp in hidden_import_list:
                command += f" --hidden-import {imp.strip()}"

        output_text.delete("1.0", tk.END)
        output_text.insert(tk.END, command)


def excute_shell():
    # command를 실행하여 콘솔 출력 결과를 캡처합니다.
    output_value = output_text.get("1.0", tk.END).strip()
    process = subprocess.Popen(output_value, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    stdout_output = []
    stderr_output = []

    def read_stdout(pipe, widget):
        while True:
            line = pipe.readline()
            if line:
                widget.insert(tk.END, line)
                widget.see(tk.END)
                stdout_output.append(line)
            else:
                break

    def read_stderr(pipe, widget):
        while True:
            line = pipe.readline()
            if line:
                widget.insert(tk.END, line)
                widget.see(tk.END)
                stderr_output.append(line)
            else:
                break

    stdout_thread = threading.Thread(target=read_stdout, args=(process.stdout, output_text))
    stderr_thread = threading.Thread(target=read_stderr, args=(process.stderr, output_text))

    stdout_thread.start()
    stderr_thread.start()

    def on_process_complete():
        process.wait()
        stdout_thread.join()
        stderr_thread.join()
        final_output = ''.join(stdout_output + stderr_output)
        messagebox.showinfo(title="알림", message="입력한 명령어가 실행 완료되었습니다.")
        print(final_output)  # 최종 출력 내용을 출력하거나 다른 용도로 사용할 수 있음

    threading.Thread(target=on_process_complete).start()

root = tk.Tk()

# 파일 경로 입력
label_path = tk.Label(root, text="py 파일 경로(py file path):")
label_path.pack()
entry_path = tk.Entry(root)
entry_path.pack()

# --onefile 체크박스
checkbox_var = tk.IntVar()
checkbox_onefile = tk.Checkbutton(root, text="한 파일로 병합(one file? )", variable=checkbox_var)
checkbox_onefile.pack()

# --noconsole 체크박스
checkbox_var2 = tk.IntVar()
checkbox_noconsole = tk.Checkbutton(root, text="콘솔 표시 안함(do not show console)", variable=checkbox_var2)
checkbox_noconsole.pack()


def get_checkbox_value():
    if checkbox_var.get() == 1:
        checkbox_ornot = "--onefile"
    else:
        checkbox_ornot = None
    return checkbox_ornot


def get_checkbox_value2():
    if checkbox_var2.get() == 1:
        checkbox_ornot_console = "--noconsole"
    else:
        checkbox_ornot_console = None
    return checkbox_ornot_console


# --hidden-import 입력
label_hidden = tk.Label(root, text="포함할 packages 입력(콤마로 구분합니다): ")
label_hidden.pack()
entry_hidden = tk.Entry(root)
entry_hidden.pack()

# 명령어 출력
button_generate = tk.Button(root, text="명령어 생성(generate command)", command=generate_command)
button_generate.pack()
generate_exe = tk.Button(root, text="exe 생성(generate exe)", command=excute_shell)
generate_exe.pack()

output_text = tk.Text(root, height=10)
output_text.pack()


def get_imported_packages(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        tree = ast.parse(file.read())
        imports = [node.names[0].name.split('.')[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
        return imports


def check_imports():
    file_path = entry_path.get().replace("'", "").replace('"', "")
    imported_packages = get_imported_packages(file_path)

    additional_output_text.delete("1.0", tk.END)
    additional_output_text.insert(tk.END, "Imported Packages:\n")
    for package in imported_packages:
        additional_output_text.insert(tk.END, f"- {package}\n")


def on_check_button_click():
    try:
        check_imports()
    except FileNotFoundError:
        messagebox.showinfo(title="알림", message="py 파일을 찾을 수 없습니다. 경로를 확인해주십시오")


check_button = tk.Button(root, text="Import 확인(check import)", command=on_check_button_click)
check_button.pack()

# import 결과창
additional_output_text = tk.Text(root, height=10)
additional_output_text.pack()

root.mainloop()
