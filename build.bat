@echo off

nuitka --standalone .\main.py --enable-plugin=pyside6 --windows-console-mode=disable --output-filename=KpsUnifier --windows-icon-from-ico=kps-unifier.ico
