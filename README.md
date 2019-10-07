# LudumDare45

LudumDare45

## Theme:

"Start with nothing"

## Description

A rogue-like where instead of starting with a class, equipment or even a body, you start with nothing...

Based in part on the LibTCOD tutorial:
http://rogueliketutorials.com/tutorials/tcod/

## PyInstaller

Using PyInstaller, run the following command inside the LudumDare45 folder to generate a standalone MacOS app:

```
pyinstaller -y --onefile --windowed --add-data 'assets/:assets' --name OurGloryShallNotDescend -i assets/images/our-glory-shall-not-descend.icns engine.py
```

Or run the following command under Windows to generate a standalone EXE:

```
pyinstaller -y --onefile --noupx --windowed --add-data "assets\;assets" --name OurGloryShallNotDescend -i assets\images\our_glory_shall_not_descend_xt8_icon.ico
```