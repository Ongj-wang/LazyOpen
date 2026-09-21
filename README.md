# LazyOpen

LazyOpen 是一个 Windows 上的项目快速打开工具。它可以把常用项目保存到一个列表中，并按你指定的方式快速打开：

- VS Code
- Qoder

项目会把 `lazylist.txt` 放在程序所在目录中，因此无论你是直接运行 Python 脚本还是打包成 EXE，配置文件都会保持在同一目录，便于管理和迁移。

## 功能特点

- 记录常用项目列表
- 按项目名快速打开
- 支持不同打开方式：`vscode` / `qoder`
- 配置文件跟程序目录绑定，打包成 EXE 后也可正常使用
- 适合在 Windows 环境中快速切换开发目录

## 目录结构

```text
LazyOpen/
├─ main.py
├─ lazylist.txt
├─ README.md
├─ build.bat
├─ lazyopen.exe   (打包后生成)
└─ ...
```

`lazylist.txt` 的格式如下：

```text
项目名|项目路径|打开方式
```

例如：

```text
welding2|E:\addon_dev\jaka_welding_kit2|qoder
```

## 用法

### 1. 添加项目

```bash
python main.py -add --name welding2 --dir "E:\addon_dev\jaka_welding_kit2" --open_method qoder
```

参数说明：

- `--name`：项目别名
- `--dir`：项目目录
- `--open_method`：打开方式，可选 `vscode` 或 `qoder`

### 2. 打开项目

```bash
python main.py -open welding2
```

### 3. 删除项目

```bash
python main.py -del welding2
```

### 4. 查看项目列表

```bash
python main.py -list
```

### 5. 查看帮助

```bash
python main.py
```

## 说明

- 如果使用 `vscode`，需要确保 `code` 命令可用，通常安装 VS Code 后会自动加入 PATH。
- 如果使用 `qoder`，需要确保 Qoder 可执行程序已安装，并且命令可被系统识别。
- `lazylist.txt` 会自动创建在脚本目录中；打包成 EXE 后，配置文件也会和 EXE 在同一目录。

## 打包成 EXE

可以使用 PyInstaller 打包：

```bash
uv run pyinstaller --onefile --windowed --name lazyopen --clean main.py
```

或者直接使用：

```bash
build.bat
```

打包后可直接运行生成的 `lazyopen.exe`。

## 示例

```bash
python main.py -add --name projectA --dir "D:\work\projectA" --open_method vscode
python main.py -open projectA
```

## 备注

这个工具适合在开发环境中快速打开常用项目，尤其适合处理多个工作目录经常切换的场景。
