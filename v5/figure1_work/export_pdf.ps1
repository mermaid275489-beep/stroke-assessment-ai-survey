$app = New-Object -ComObject PowerPoint.Application
$p = $app.Presentations.Open("D:\Stroke\v5\figure1_work\Figure1_revised.pptx", $true, $false, $false)
$p.SaveAs("D:\Stroke\v5\figure1_work\Figure1_revised_fullslide.pdf", 32)
$p.Close()
$app.Quit()
"pdf exported"
