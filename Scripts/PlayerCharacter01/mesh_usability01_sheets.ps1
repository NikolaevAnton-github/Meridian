Add-Type -AssemblyName System.Drawing
$meshRoot = Join-Path $PSScriptRoot '../../Saved/PlayerCharacter01/MeshUsability01/Worker'
$meshOut = Join-Path $meshRoot 'Sheets'
New-Item -ItemType Directory -Force $meshOut | Out-Null
$meshFont = New-Object System.Drawing.Font('Arial',11)
foreach ($meshSet in @('Detail05','DeformationBind05Final')) {
    $meshFiles = @(Get-ChildItem (Join-Path $meshRoot $meshSet) -Filter '*.png' | Sort-Object Name)
    for ($meshStart=0; $meshStart -lt $meshFiles.Count; $meshStart+=16) {
        $meshBitmap = New-Object System.Drawing.Bitmap(1440,1560)
        $meshGraphics = [System.Drawing.Graphics]::FromImage($meshBitmap)
        $meshGraphics.Clear([System.Drawing.Color]::FromArgb(40,40,40))
        for ($meshIndex=0; $meshIndex -lt 16 -and ($meshStart+$meshIndex) -lt $meshFiles.Count; $meshIndex++) {
            $meshFile=$meshFiles[$meshStart+$meshIndex]
            $meshImage=[System.Drawing.Image]::FromFile($meshFile.FullName)
            $meshX=($meshIndex % 4)*360; $meshY=[math]::Floor($meshIndex/4)*390
            $meshGraphics.DrawImage($meshImage,[int]$meshX,[int]$meshY,360,360)
            $meshGraphics.DrawString($meshFile.BaseName,$meshFont,[System.Drawing.Brushes]::White,[single]($meshX+4),[single]($meshY+360))
            $meshImage.Dispose()
        }
        $meshBitmap.Save((Join-Path $meshOut ($meshSet+'-'+([int]($meshStart/16)+1)+'.png')),[System.Drawing.Imaging.ImageFormat]::Png)
        $meshGraphics.Dispose();$meshBitmap.Dispose()
    }
}
$meshFont.Dispose()
