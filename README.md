# FDS Extractor

![icon](bottle.ico)

FDS Extractor is an application that retrieves codes from chemical product safety data sheets.

## Run the project

```sh
python3 src/fds-extractor.py
```

## Build the project

```sh
python3 -m PyInstaller --add-data "path/to/pypdfium2_raw/pdfium.dll;pypdfium2_raw" --add-data "path/to/pypdfium2_raw/version.json;pypdfium2_raw" --add-data "path/to/pypdfium2/version.json;pypdfium2" --noconsole --onefile --windowed --icon=bottle.ico ./src/fds-extractor.py
```
