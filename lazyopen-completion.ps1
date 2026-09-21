$completionScript = {
    param($wordToComplete, $commandAst, $cursorPosition)

    $commandText = $commandAst.Extent.Text
    if ($commandText -notmatch "(?i)(^|\s)-(open|folder|del)(\s|$)") {
        return
    }

    $listFile = Join-Path $PSScriptRoot "lazylist.txt"
    if (Test-Path $listFile) {
        Get-Content $listFile -ErrorAction SilentlyContinue |
            ForEach-Object {
                $projectName = ($_ -split "\|", 2)[0]
                if ($projectName -and $projectName.StartsWith($wordToComplete, [System.StringComparison]::OrdinalIgnoreCase)) {
                    [System.Management.Automation.CompletionResult]::new(
                        $projectName, $projectName, "ParameterValue", $projectName
                    )
                }
            }
        }
}

Register-ArgumentCompleter -Native -CommandName lazyopen -ScriptBlock $completionScript
Register-ArgumentCompleter -Native -CommandName lazyopen.exe -ScriptBlock $completionScript