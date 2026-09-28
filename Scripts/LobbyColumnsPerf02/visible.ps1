param([int]$EditorPid)
Add-Type @'
using System;
using System.Runtime.InteropServices;
public class Perf02Window {
    [DllImport("user32.dll")] public static extern bool ShowWindowAsync(IntPtr hWnd, int cmd);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool IsIconic(IntPtr hWnd);
}
'@
$editor = Get-Process -Id $EditorPid
if ($editor.MainWindowHandle -eq 0) { throw 'Editor window not ready' }
[Perf02Window]::ShowWindowAsync($editor.MainWindowHandle, 9) | Out-Null
[Perf02Window]::SetForegroundWindow($editor.MainWindowHandle) | Out-Null
@{ pid=$EditorPid; minimized=[Perf02Window]::IsIconic($editor.MainWindowHandle); handle=$editor.MainWindowHandle.ToInt64() } | ConvertTo-Json
