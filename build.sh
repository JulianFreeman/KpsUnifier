#!/bin/zsh

pyinstaller -D -w -i ../kps-unifier.icns --workpath build/build --distpath build/dist --specpath build --name KpsUnifier main.py
