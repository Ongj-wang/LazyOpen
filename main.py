import os
import shutil
import subprocess
import sys
from pathlib import Path


def get_app_dir():
    """返回脚本/EXE 所在目录，确保 lazylist.txt 与程序放在同一目录。"""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent.parent
    return Path(__file__).resolve().parent


APP_DIR = get_app_dir()
LAZYLIST_FILE = APP_DIR / "lazylist.txt"


def find_executable(candidates):
    """查找可执行文件，兼容 Windows 下的 .cmd/.bat 包装器，以及 Linux/macOS 的编辑器入口。"""
    for candidate in candidates:
        if not candidate:
            continue
        if os.path.exists(candidate):
            return candidate
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    return None


def get_editor_candidates(method):
    """返回各平台下的编辑器候选命令，兼容 VS Code、VS Code Insiders、Cursor、Qoder 等。"""
    if method == "qoder":
        return [
            "qoder",
            "Qoder",
            "Qoder IDE",
            "Qoder IDE.exe",
            "qoder.exe",
        ]

    if os.name == "nt":
        return [
            "code",
            "code-insiders",
            "cursor",
            "code.cmd",
            "code.exe",
            os.path.join(
                os.environ.get("LOCALAPPDATA", ""),
                "Programs",
                "Microsoft VS Code",
                "bin",
                "code.cmd",
            ),
            os.path.join(
                os.environ.get("ProgramFiles", ""),
                "Microsoft VS Code",
                "bin",
                "code.cmd",
            ),
            os.path.join(
                os.environ.get("ProgramFiles(x86)", ""),
                "Microsoft VS Code",
                "bin",
                "code.cmd",
            ),
            os.path.join(
                os.environ.get("LOCALAPPDATA", ""),
                "Programs",
                "Cursor",
                "resources",
                "app",
                "bin",
                "cursor.cmd",
            ),
        ]

    if sys.platform == "darwin":
        return [
            "code",
            "code-insiders",
            "cursor",
            "/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code",
            "/Applications/Visual Studio Code - Insiders.app/Contents/Resources/app/bin/code",
            "/Applications/Cursor.app/Contents/MacOS/Cursor",
        ]

    return [
        "code",
        "code-insiders",
        "cursor",
        "cursor-insiders",
        "codium",
        "code-oss",
        "/usr/bin/code",
        "/usr/local/bin/code",
        "/snap/bin/code",
        "/usr/share/code/bin/code",
        "/usr/bin/code-insiders",
        "/usr/local/bin/code-insiders",
    ]


def build_open_command(method, project_dir, new_window=False):
    """构造打开命令列表，兼容 VS Code / Qoder 的 Windows / Linux / macOS 启动方式。
    如果 new_window=True，则尽可能传递打开新窗口的参数（例如 VS Code 的 `-n`）。"""
    executable = find_executable(get_editor_candidates(method))

    if not executable:
        return None

    # 对于不同编辑器/IDE，添加打开新窗口的参数
    if method == "vscode":
        if new_window:
            return [executable, "-n", project_dir]
        return [executable, project_dir]
    # qoder 暂无统一的新窗口参数，直接传目录
    return [executable, project_dir]


def load_projects():
    """加载项目列表"""
    if not LAZYLIST_FILE.exists():
        return []
    projects = []
    with LAZYLIST_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split("|")
            if len(parts) == 3:
                projects.append({"name": parts[0], "dir": parts[1], "method": parts[2]})
    return projects


def save_projects(projects):
    """保存项目列表"""
    with LAZYLIST_FILE.open("w", encoding="utf-8") as f:
        for p in projects:
            f.write(f"{p['name']}|{p['dir']}|{p['method']}\n")


def add_project(name, proj_dir, method):
    """添加项目"""
    if not name or not proj_dir:
        print("❌ 错误: 必须指定项目名称 (--name) 和项目路径 (--dir)")
        return
    proj_path = Path(proj_dir).expanduser()
    if not proj_path.is_dir():
        print(f"❌ 错误: 目录不存在: {proj_dir}")
        return

    # 规范化路径，去掉末尾的反斜杠
    proj_dir = str(proj_path.resolve())

    projects = load_projects()
    for p in projects:
        if p["name"].lower() == name.lower():
            print(f"❌ 错误: 项目 '{name}' 已存在，请先删除再添加")
            return

    method = method.lower() if method else "vscode"
    if method not in ["vscode", "qoder"]:
        method = "vscode"

    projects.append({"name": name, "dir": proj_dir, "method": method})
    save_projects(projects)
    print(f"✅ 已添加项目: {name}")
    print(f"   路径: {proj_dir}")
    print(f"   打开方式: {method}")


def open_project(name, open_method=None):
    """打开项目"""
    if not name:
        print("❌ 错误: 请指定项目名称")
        return

    projects = load_projects()
    target = None
    for p in projects:
        if p["name"].lower() == name.lower():
            target = p
            break

    if not target:
        print(f"❌ 错误: 未找到项目 '{name}'")
        list_projects()
        return

    target_dir = Path(target["dir"]).expanduser()
    if not target_dir.is_dir():
        print(f"❌ 错误: 项目目录不存在: {target['dir']}")
        return
    if open_method:
        target["method"] = open_method
    print(f"🚀 正在用 {target['method']} 打开项目 '{target['name']}'...")
    command = build_open_command(target["method"], str(target_dir))
    if not command:
        print(
            f"❌ 错误: 未在系统 PATH 中找到 '{target['method']}' 命令，请确认已安装或已添加到环境变量"
        )
        return

    try:
        # Windows 上若是 .cmd/.bat，使用 shell=True 并把所有参数拼为一个命令行字符串
        if os.name == "nt" and os.path.splitext(command[0])[1].lower() in {
            ".cmd",
            ".bat",
        }:
            cmdline = " ".join(f'"{p}"' for p in command)
            subprocess.Popen(cmdline, shell=True)
        else:
            subprocess.Popen(command)
        print("✅ 已发送打开指令")
    except OSError as exc:
        print(f"❌ 错误: 启动 {target['method']} 失败: {exc}")


def open_folder(folder_path, open_method=None):
    """直接打开指定文件夹，支持在系统文件管理器或编辑器中打开。"""
    if not folder_path:
        print("❌ 错误: 请指定文件夹路径")
        return

    folder = Path(folder_path).expanduser()
    if not folder.is_dir():
        print(f"❌ 错误: 目录不存在: {folder_path}")
        return

    normalized_method = (open_method or "").lower()
    if normalized_method in {"vscode", "qoder"}:
        try:
            command = build_open_command(normalized_method, str(folder))
            if not command:
                print(
                    f"❌ 错误: 未在系统 PATH 中找到 '{normalized_method}' 命令，请确认已安装或已添加到环境变量"
                )
                return
            subprocess.Popen(command)
            print(f"✅ 已在 {normalized_method} 中打开: {str(folder)}")
        except OSError as exc:
            print(f"❌ 错误: 启动 {normalized_method} 失败: {exc}")
        return

    # 使用系统默认文件管理器打开
    try:
        if os.name == "nt":
            os.startfile(str(folder))
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(folder)])
        else:
            subprocess.Popen(["xdg-open", str(folder)])
        print(f"✅ 已在文件资源管理器中打开: {str(folder)}")
    except OSError as exc:
        print(f"❌ 错误: 无法使用文件管理器打开目录: {exc}")
    return


def del_project(name):
    """删除项目"""
    if not name:
        print("❌ 错误: 请指定项目名称")
        return

    projects = load_projects()
    new_projects = [p for p in projects if p["name"].lower() != name.lower()]

    if len(new_projects) == len(projects):
        print(f"❌ 错误: 未找到项目 '{name}'")
    else:
        save_projects(new_projects)
        print(f"🗑️ 已删除项目: {name}")


def list_projects():
    """列出所有项目"""
    projects = load_projects()
    if not projects:
        print("📂 lazylist.txt 为空，还没有添加任何项目")
        return

    print("\n" + "=" * 50)
    print(" 已保存的项目列表")
    print("=" * 50)
    for i, p in enumerate(projects, 1):
        print(f" [{i}] {p['name']}")
        print(f"     路径: {p['dir']}")
        print(f"     打开方式: {p['method']}")
        print()
    print("=" * 50)
    print(f"共 {len(projects)} 个项目")


def complete_projects(prefix):
    """输出匹配的项目名，供终端补全器调用。"""
    prefix = (prefix or "").lower()
    for project in load_projects():
        if project["name"].lower().startswith(prefix):
            print(project["name"])


def print_help():
    """打印帮助信息"""
    print("\n" + "=" * 50)
    print(" LazyOpen - 快速打开项目工具 (Python版)")
    print("=" * 50)
    print("\n用法:")
    print("  python lazyopen.py -open <项目名>")
    print(
        "  python lazyopen.py -add --name <名> --dir <路径> [--open_method vscode|qoder]"
    )
    print("  python lazyopen.py -del <项目名>")
    print("  python lazyopen.py -list")
    print(
        "  python lazyopen.py -folder <项目名>  # 在文件资源管理器中打开（默认），或指定 vscode|qoder 在编辑器中打开"
    )
    print("\n示例:")
    print(
        '  python lazyopen.py -add --name welding2 --dir "E:\\addon_dev\\jaka_welding_kit2" --open_method qoder'
    )
    print("  python lazyopen.py -open welding2")
    print("=" * 50)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_help()
        sys.exit(0)
    action = sys.argv[1].lower()

    if action == "-complete":
        complete_projects(sys.argv[2] if len(sys.argv) > 2 else "")

    elif action == "-add":
        # 解析参数
        name = None
        proj_dir = None
        method = "vscode"
        i = 2
        while i < len(sys.argv):
            arg = sys.argv[i]
            if arg == "--name" and i + 1 < len(sys.argv):
                name = sys.argv[i + 1]
                i += 2
            elif arg == "--dir" and i + 1 < len(sys.argv):
                proj_dir = sys.argv[i + 1]
                i += 2
            elif arg == "--open_method" and i + 1 < len(sys.argv):
                method = sys.argv[i + 1]
                i += 2
            else:
                i += 1
        add_project(name, proj_dir, method)

    elif action == "-open":
        name = sys.argv[2] if len(sys.argv) > 2 else None
        open_method = sys.argv[3] if len(sys.argv) > 3 else None
        open_project(name, open_method)

    elif action == "-folder":
        # 第二个参数为项目名，类似 -open 行为；可选第三个参数覆盖打开方式（vscode|qoder）
        name = sys.argv[2] if len(sys.argv) > 2 else None
        open_method = sys.argv[3] if len(sys.argv) > 3 else None
        if not name:
            print("❌ 错误: 请指定项目名称")
            sys.exit(1)

        projects = load_projects()
        target = None
        for p in projects:
            if p["name"].lower() == name.lower():
                target = p
                break

        if not target:
            print(f"❌ 错误: 未找到项目 '{name}'")
            list_projects()
            sys.exit(1)

        proj_dir = Path(target["dir"]).expanduser()
        if not proj_dir.is_dir():
            print(f"❌ 错误: 项目目录不存在: {target['dir']}")
            sys.exit(1)

        open_folder(str(proj_dir), open_method)

    elif action == "-del":
        name = sys.argv[2] if len(sys.argv) > 2 else None
        del_project(name)

    elif action == "-list":
        list_projects()
    else:
        print(f"❌ 未知命令: {action}")
        print_help()
