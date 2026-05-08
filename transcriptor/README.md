# Transcriptor Local de Video a SRT

Herramienta local para cargar videos cortos, transcribirlos con Whisper y exportar subtitulos `.srt` compatibles con DaVinci Resolve.

## Requisitos

- Windows 10/11.
- Python 3.10 o superior.
- FFmpeg instalado y disponible en `PATH`.

Para verificar FFmpeg en PowerShell:

```powershell
ffmpeg -version
ffprobe -version
```

Si esos comandos no funcionan, instala FFmpeg con Winget:

```powershell
winget install Gyan.FFmpeg
```

Cierra y vuelve a abrir PowerShell despues de instalarlo.

## Instalacion

Desde la carpeta del proyecto:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

La primera transcripcion descargara el modelo Whisper seleccionado. El modelo `base` es un buen punto de partida; `small` suele ser mas preciso, pero tarda mas.

## Uso

Ejecuta la interfaz:

```powershell
streamlit run src/transcriptor_app/app.py
```

Luego:

1. Carga un video de hasta 5 minutos.
2. Elige el modelo y el idioma. Para videos en espanol usa `es`.
3. Haz clic en `Transcribir video`.
4. Corrige el texto en el editor SRT si hace falta.
5. Descarga el archivo `.srt`.

## Crear ejecutable para Windows

Puedes generar un `.exe` con PyInstaller:

```powershell
.\scripts\build_exe.ps1
```

El ejecutable quedara en:

```text
dist_app\TranscriptorLocal\TranscriptorLocal.exe
```

Al abrirlo, iniciara la aplicacion en `http://localhost:8501` y mostrara la interfaz en el navegador. El equipo donde lo uses tambien debe tener FFmpeg instalado y disponible en `PATH`.

## Importar en DaVinci Resolve

En DaVinci Resolve puedes importar el `.srt` como subtitulos desde el Media Pool o arrastrarlo a la linea de tiempo. Si el video empieza en un punto distinto al inicio de la timeline, ajusta la posicion del clip de subtitulos para sincronizarlo.

## Pruebas

```powershell
pytest
```

## Notas

- Todo el procesamiento ocurre localmente en tu PC.
- La calidad depende del audio original y del modelo elegido.
- Si usas CPU y encuentras problemas con la configuracion por defecto, prueba la precision `int8` en la barra lateral.

