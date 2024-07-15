# FDS Extractor

![icon](bottle.ico)

FDS Extractor is an application that retrieves codes from chemical product safety data sheets.

## Run the project

```sh
python3 src/fds-extractor.py
```

## Build the project

```sh
pip install nuitka
```

```sh
python3 -m nuitka --mingw64 --standalone --windows-console-mode=disable --enable-plugin=pyqt5 --windows-icon-from-ico=bottle.ico --onefile ./src/fds-extractor.py
```
