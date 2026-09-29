$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\.." )).Path

$completionScript = {
    param($wordToComplete, $commandAst, $cursorPosition)

    $commandText = $commandAst.Extent.Text
    if ($commandText -notmatch "(?i)(^|\s)-(open|folder|del|terminal|teminal|t)(\s|$)") {
        return
    }

    $listFile = Join-Path $projectRoot "lazylist.txt"
    if (Test-Path $listFile) {
        Get-Content $listFile -Encoding UTF8 -ErrorAction SilentlyContinue |
            ForEach-Object {
                $projectName = ($_ -split "\|", 2)[0]
                if ($projectName -and $projectName.StartsWith($wordToComplete, [System.StringComparison]::OrdinalIgnoreCase)) {
                    [System.Management.Automation.CompletionResult]::new(
                        $projectName, $projectName, "ParameterValue", $projectName
                    )
                }
            }
        }
}.GetNewClosure()

Register-ArgumentCompleter -Native -CommandName lazyopen -ScriptBlock $completionScript
Register-ArgumentCompleter -Native -CommandName lazyopen.exe -ScriptBlock $completionScript