$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$DistPath = Join-Path $ProjectRoot "dist_app"
$WorkPath = Join-Path $ProjectRoot "build_app"

if (-not (Test-Path $Python)) {
    Write-Host "Creando entorno virtual..."
    python -m venv (Join-Path $ProjectRoot ".venv")
}

Write-Host "Instalando dependencias..."
& $Python -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) {
    throw "No se pudo actualizar pip."
}
& $Python -m pip install -e "$ProjectRoot[dev]"
if ($LASTEXITCODE -ne 0) {
    throw "No se pudieron instalar las dependencias."
}

Write-Host "Construyendo ejecutable..."
& $Python -m PyInstaller `
    --noconfirm `
    --clean `
    --name "TranscriptorLocal" `
    --distpath $DistPath `
    --workpath $WorkPath `
    --paths (Join-Path $ProjectRoot "src") `
    --add-data "$ProjectRoot\src\transcriptor_app\app.py;transcriptor_app" `
    --collect-all streamlit `
    --collect-all faster_whisper `
    --collect-all ctranslate2 `
    --hidden-import transcriptor_app.app `
    --hidden-import transcriptor_app.transcription `
    --hidden-import transcriptor_app.srt `
    --hidden-import transcriptor_app.config `
    (Join-Path $ProjectRoot "src\transcriptor_app\launcher.py")
if ($LASTEXITCODE -ne 0) {
    throw "No se pudo construir el ejecutable. Cierra TranscriptorLocal.exe y cualquier ventana de la app antes de intentarlo de nuevo."
}

Write-Host ""
Write-Host "Ejecutable listo en:"
Write-Host (Join-Path $DistPath "TranscriptorLocal\TranscriptorLocal.exe")
Write-Host ""
Write-Host "Recuerda instalar FFmpeg en el equipo donde uses el ejecutable."

