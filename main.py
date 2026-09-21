import os
import shutil
import subprocess
import sys
from pathlib import Path


def get_app_dir():
    """返回脚本/EXE 所在目录，确保 lazylist.txt 与程序放在同一目录。"""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


APP_DIR = get_app_dir()
LAZYLIST_FILE = APP_DIR / "lazylist.txt"


def find_executable(candidates):
    """查找可执行文件，兼容 Windows 下的 .cmd/.bat 包装器。"""
    for candidate in candidates:
        if not candidate:
            continue
        if os.path.exists(candidate):
            return candidate
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    return None


def build_open_command(method, project_dir):
    """构造打开命令列表，兼容 VS Code / Qoder 的 Windows 启动方式。"""
    if method == "qoder":
        executable = find_executable(
            [
                "qoder",
                "Qoder",
                "Qoder IDE",
                "Qoder IDE.exe",
                "qoder.exe",
            ]
        )
    else:
        executable = find_executable(
            [
                "code",
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
            ]
        )

    if not executable:
        return None
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


def open_project(name):
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

    print(f"🚀 正在用 {target['method']} 打开项目 '{target['name']}'...")

    command = build_open_command(target["method"], str(target_dir))
    if not command:
        print(
            f"❌ 错误: 未在系统 PATH 中找到 '{target['method']}' 命令，请确认已安装或已添加到环境变量"
        )
        return

    try:
        if os.name == "nt" and os.path.splitext(command[0])[1].lower() in {
            ".cmd",
            ".bat",
        }:
            subprocess.Popen(f'"{command[0]}" "{command[1]}"', shell=True)
        else:
            subprocess.Popen(command)
        print("✅ 已发送打开指令")
    except OSError as exc:
        print(f"❌ 错误: 启动 {target['method']} 失败: {exc}")


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
    print(f"sys.argv: {sys.argv}")
    action = sys.argv[1].lower()

    if action == "-add":
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
        open_project(name)

    elif action == "-del":
        name = sys.argv[2] if len(sys.argv) > 2 else None
        del_project(name)

    elif action == "-list":
        list_projects()

    else:
        print(f"❌ 未知命令: {action}")
        print_help()
