# LudumDare45

LudumDare45

## Theme:

"Start with nothing"

## Description

A rogue-like where instead of starting with a class, equipment or even a body, you start with nothing...

Based in part on the LibTCOD tutorial:
http://rogueliketutorials.com/tutorials/tcod/

## Binaries

The latest Mac apps and Windows .exe builds are available here:

https://github.com/sbackus/LudumDare45/releases/latest

## From Source

From inside the LudumDare45 folder:

Install the dependencies from requirements.txt using pip:

```
cd LudumDare45
pip install -r requirements.xt
```

Or Using [Pipenv](https://pipenv-fork.readthedocs.io/en/latest/index.html):

```
cd LudumDare45
pipenv install
```

Then you should be able to start the game by running engine.py:

```
python engine.py
```

Or with Pipenv:

```
pipenv run python engine.py

    (or)

pipenv shell
python engine.py
exit # (to leave pipenv shell)
```

## Building Binary Packages with PyInstaller

In addition to the above, make sure you have development packages installed:

Pip:
```
pip install -r dev-requirements.txt
```

Pipenv:
```
pipenv install -d
```

(Note that PyInstaller must be run in the operating system and environment being packaged!)

In MacOS: Run the following command inside the LudumDare45 folder to generate a standalone app:

```
pyinstaller -y --onefile --windowed --add-data 'assets/:assets' --name OurGloryShallNotDescend -i assets/images/our-glory-shall-not-descend.icns engine.py
```

In Windows: Run the following command inside the LudumDare45 folder to generate a standalone exe:

```
pyinstaller -y --onefile --noupx --windowed --add-data "assets\;assets" --name OurGloryShallNotDescend -i assets\images\our_glory_shall_not_descend_xt8_icon.ico
```

If successful, the new binary should be available in the /dist folder.
