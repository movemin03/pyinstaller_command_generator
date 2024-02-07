import tkinter as tk
import subprocess
import ast

def generate_command():
    file_path = entry_path.get().replace("'", "").replace('"', "")
    one_file = get_checkbox_value()
    hidden_import = entry_hidden.get()

    command = "pyinstaller"
    command += f" {file_path}"
    if one_file:
        command += f" {one_file}"

    if hidden_import:
        hidden_import_list = hidden_import.split(",")
        for imp in hidden_import_list:
            command += f" --hidden-import {imp.strip()}"

    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, command)


root = tk.Tk()

# 파일 경로 입력
label_path = tk.Label(root, text="파일 경로(file path):")
label_path.pack()
entry_path = tk.Entry(root)
entry_path.pack()

# --onefile 체크박스
checkbox_var = tk.IntVar()
checkbox_onefile = tk.Checkbutton(root, text="한 파일로 병합(one file or not)", variable=checkbox_var)
checkbox_onefile.pack()


def get_checkbox_value():
    if checkbox_var.get() == 1:
        checkbox_ornot = "--onefile"
    else:
        checkbox_ornot = None
    return checkbox_ornot

# --hidden-import 입력
label_hidden = tk.Label(root, text="포함할 packages 입력(콤마로 구분합니다): ")
label_hidden.pack()
entry_hidden = tk.Entry(root)
entry_hidden.pack()

# 명령어 출력
button_generate = tk.Button(root, text="명령어 생성(generate)", command=generate_command)
button_generate.pack()

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
    check_imports()

check_button = tk.Button(root, text="Import 확인(check import)", command=on_check_button_click)
check_button.pack()

#import 결과창
additional_output_text = tk.Text(root, height=10)
additional_output_text.pack()

root.mainloop()
