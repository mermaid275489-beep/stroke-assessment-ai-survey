param([string]$name = "Figure1_original")
$dir = "D:\Stroke\v5\figure1_work"
$src = Join-Path $dir "$name.pptx"
$png = Join-Path $dir "$name.png"
$app = New-Object -ComObject PowerPoint.Application
$p = $app.Presentations.Open($src, $true, $false, $false)
$w = $p.PageSetup.SlideWidth; $h = $p.PageSetup.SlideHeight
"slide size pt: $w x $h"
$p.Slides(1).Export($png, "PNG", 3000, [int](3000 * $h / $w))
foreach ($s in $p.Slides(1).Shapes) {
  $t = ""
  if ($s.HasTextFrame -and $s.TextFrame.HasText) {
    $tr = $s.TextFrame.TextRange
    $t = ($tr.Text -replace "`r", " | ")
    $sz = $tr.Font.Size
    $flag = ""
    if ($tr.BoundWidth -gt $s.Width + 1) { $flag = "OVERFLOW" }
    "{0}`t{1:N0},{2:N0},{3:N0}x{4:N0}`t{5}pt`t{6}`t{7}" -f $s.Name, $s.Left, $s.Top, $s.Width, $s.Height, $sz, $flag, $t
  } else {
    "{0}`t{1:N0},{2:N0},{3:N0}x{4:N0}`t[{5}]" -f $s.Name, $s.Left, $s.Top, $s.Width, $s.Height, $s.Type
  }
}
$p.Close()
$app.Quit()
