@echo off

pyinstaller -D -w -i ..\kps-unifier.ico --workpath .\build\build --distpath .\build\dist --specpath .\build --name KpsUnifier .\main.py
