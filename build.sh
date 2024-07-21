#!/bin/zsh

python -m nuitka --macos-create-app-bundle --windows-console-mode=disable --enable-plugin=pyside6 --macos-app-icon=kps-unifier.icns --macos-app-name=KpsUnifier --output-filename=KpsUnifier --remove-output ./main.py
