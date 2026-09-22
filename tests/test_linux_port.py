from main import build_open_command


def test_build_open_command_accepts_linux_vscode_aliases(monkeypatch):
    def fake_which(command):
        linux_commands = {
            "code-insiders": "/usr/bin/code-insiders",
            "cursor": "/usr/bin/cursor",
        }
        return linux_commands.get(command)

    monkeypatch.setattr("main.shutil.which", fake_which)

    command = build_open_command("vscode", "/tmp/demo-project", new_window=True)

    assert command is not None
    assert command[0] in {"/usr/bin/code-insiders", "/usr/bin/cursor"}
    assert command[1] == "-n"
    assert command[2] == "/tmp/demo-project"
