# LazyOpen

LazyOpen 是一个跨平台的项目快速打开工具。它可以把常用项目保存到一个列表中，并按你指定的方式快速打开：

- VS Code / VS Code Insiders / Cursor
- Qoder

它同样适用于 Linux、macOS 和 Windows 环境。
项目会把 `lazylist.txt` 放在仓库根目录中，所有平台共用同一个配置文件，便于管理和迁移。

## 功能特点

- 记录常用项目列表
- 按项目名快速打开
- 支持不同打开方式：`vscode` / `qoder`
- 配置文件跟程序目录绑定，打包成 EXE 后也可正常使用
- 适合在跨平台开发环境中快速切换开发目录

## 目录结构

```text
LazyOpen/
├─ main.py
├─ lazylist.txt
├─ README.md
├─ deploy.bat
├─ deploy.sh
├─ linux/
│  ├─ lazyopen
│  └─ AutoRegistration/
│     ├─ lazyopen-completion.bash
│     └─ lazyopen-completion.zsh
├─ windows/
│  ├─ lazyopen.bat
│  └─ AutoRegistration/
│     └─ lazyopen-completion.ps1
└─ tests/
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

在 Windows PowerShell 中，可以让 `-open`、`-folder` 和 `-del` 后的项目名使用 Tab 自动补全。执行 `deploy.bat` 时会自动把补全脚本加入 PowerShell 的 `$PROFILE`，以后打开新 PowerShell 窗口即可使用。

如果没有执行部署脚本，也可以手动加载一次：

```powershell
. .\windows\AutoRegistration\lazyopen-completion.ps1
```

之后输入 `lazyopen -open <Tab>`、`lazyopen -folder <Tab>` 或 `lazyopen -del <Tab>` 即可补全 `lazylist.txt` 中的项目名。若希望每次打开 PowerShell 都生效，请将这行加入 `$PROFILE`。

Linux / macOS 下可使用：

```bash
. ./linux/AutoRegistration/lazyopen-completion.bash
# 或
. ./linux/AutoRegistration/lazyopen-completion.zsh
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

### 6. 在文件资源管理器中打开项目目录（新）

新增 `-folder` 命令：行为类似 `-open`，但用于在系统文件资源管理器中直接打开项目所在的文件夹。

- 用法：

```bash
python main.py -folder <项目名> [open_method]
```

- 说明：
  - 第二个参数是已保存的 `项目名`（从 `lazylist.txt` 查找项目路径）。
  - 如果不指定 `open_method`（第三个参数），默认会在系统的文件资源管理器中打开该目录（Windows 使用资源管理器，mac 使用 `open`，Linux 使用 `xdg-open`）。
  - 可以通过第三个参数指定 `vscode` 或 `qoder`，则会在对应编辑器中打开该目录。例如：

```bash
python main.py -folder welding          # 在文件资源管理器中打开 'welding' 项目的目录
python main.py -folder welding vscode   # 在 VS Code 中打开该目录（等同于在编辑器中打开）
```

## 说明

- 如果使用 `vscode`，需要确保 `code` 命令可用，通常安装 VS Code 后会自动加入 PATH。
- 如果使用 `qoder`，需要确保 Qoder 可执行程序已安装，并且命令可被系统识别。
- `lazylist.txt` 会保存在项目根目录中，所有脚本共用同一个配置文件。

## 直接运行

不需要打包成 EXE，直接用 Python 执行即可：

```bash
python main.py -list
python main.py -add --name projectA --dir "/path/to/projectA" --open_method vscode
python main.py -open projectA
```

也可以直接使用平台包装脚本：

```bash
./linux/lazyopen -list
./linux/lazyopen -open projectA
```

Windows 下可直接运行：

```bat
windows\lazyopen.bat -list
windows\lazyopen.bat -open projectA
```

## 一键部署

Windows：

```bash
deploy.bat
```

Linux / macOS：

```bash
chmod +x deploy.sh
./deploy.sh
```

部署脚本会依次完成以下操作：

- 将对应平台的包装脚本加入当前用户的 `PATH`
- 注册 Bash/Zsh 或 PowerShell 补全脚本
- 让终端可以直接执行 `lazyopen` 命令

PATH 更新后请重新打开终端，即可直接执行 `lazyopen` 命令。

## 示例

```bash
python main.py -add --name projectA --dir "D:\work\projectA" --open_method vscode
python main.py -open projectA
```

## 备注

这个工具适合在开发环境中快速打开常用项目，尤其适合处理多个工作目录经常切换的场景。
