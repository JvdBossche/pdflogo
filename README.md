# pdflogo
A small Python tool with a GUI to add a logo to a PDF document.

A PNG, JPG or even another PDF can be used as "logo" to be added to the input PDF.

There are options to define where the logo should end up:
 * X/Y coordinates
 * first page
 * repeat every n pages

These settings, as well the path of the last used logo, are remembered for the next run.


The GUI interface is in Dutch since that is the target audience. But the code is in English so translating should be trivial. No I8n effort was done at all.

## Installation (on Windows)
These instruction are specific to the NPO this was created for: hey are using Windows 11.
### Python
Surf to https://www.python.org/downloads/ and click "Download Python 3.10...."

Start the downloaded installation program.

In the installer, uncheck the box of `Install lancher for all users` unless you are an administrator on you computer or know the password to an administrative account.

Also add a check in front of `Add Python 3.10 to PATH`.

Click `Install Now`.

A few seconds later, close the installation.

Restart the computer, in order to get the path settings (a.o.) propagated correctly.

### PDFlogo itself
Python is a language that uses interpreted code files. That is: you actually run the *code* "directly", not a built executable version of it.

The code of the program is very small, but it needs a couple of (big) libraries, these are installed at a command prompt, by using the commands listed below.

To open a command prompt, click the Start button and type `cmd` to search for it. Open the found Command Prompt app and enter the commands below, each one terminated by the Enter key.
Some commands do not give any feedback, apart from showing another prompt where you can paste in the next command.

```
cd \
py -m pip install --upgrade pip
py -m venv c:\pdflogo
cd pdflogo 
.\Scripts\activate
py -m pip install --upgrade pip
py -m pip install --upgrade PyMuPDF
py -m pip install --upgrade PySimpleGUI
```
This will
1) Go to the root folder of the drive
2) Upgrade the `pip` tool of Python (for the entire Python installation)
3) Crearte a new directory (`c:\pdflogo`) which is a new Python Virtual Environment (`venv`). This means that all versions of Python itself and aditionally installed packages will remain stable *within that environment* (directory)
4) Enter that new directory
5) Activate the environment: *use it*, as opposed to using the overall Python installation.
6) Upgrade `pip` again, now inside the `venv`.
7) Use the freshly upgraded pip to install the `PyMuPDF` package: this is for working with PDF-files.
8) And also install `PySimpleGUI`. A package for making simple Graphical User Interfaces using Python.

Next, download the files from this repository and add them to the pdflogo folder. You'll have the `c:\pdflogo` directory opened in the File Explorer for this.

You need
 - `pdflogo.pyw` (the program)
 - `pdflogo.bat` (automatically activates the environment before startng the program)
 
 Right-click the `pdflogo.bat` file (in the `C:\pdflogo`-directory) and select `Send to` > `Desktop (create shortcut)`
 
 Now  go to the Desktop and richt-click the freshly created shortcut. Choose `Properties`.
 
 The `Target` and `Start in`-folder should both be c:\pdflogo.
 
 For `Run` select `Minimized`: the batch file will now not be visible, only the PDFlogo GUI itself.
 
 Doubleclick the shortcut to launch the program.
 
 
