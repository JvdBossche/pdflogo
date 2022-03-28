# pdflogo2.pyw

from tkinter import NONE #Use wrapper PySimpleGUI instead
import PySimpleGUI as sg

import fitz #a.k.a. PyMuPDF, to work with PDFs

import os.path
from pathlib import Path
import sys

debug=True
def dPrint(*args, **kwargs):
    """
    Asimple wrapper around sg.Print().
    It prints only when the global debug variable is set to True
    => build a release version without the debug window. :)
    """
    if debug:
        sg.Print(*args, **kwargs)


"""
Objects used throughout the program (Global variables)
"""
settings = {}
pdfin_path = ""
src_pdf = fitz.open(None)
dPrint(f"src_pdf.name: {src_pdf.name}")
logo = fitz.open(None)
dPrint(f"logo.name: {logo.name}")
pdfout_path = ""
dst_pdf = fitz.open(None)
dPrint(f"dst_pdf.name: {dst_pdf.name}")

def getsettings():
    global settings
    # Try to get the last used logo from the user settings
    settings["-us_logoin-"] = sg.user_settings_get_entry("-us_logoin-", "")
    # Try to get the last used logo position from the user settings
    settings["-us_logopos-"] = sg.user_settings_get_entry("-us_logopos-",
        {"x1": None, "y1": None, "x2": None, "y2": None})
    # try to get the last start and step page indicators from the user settings
    settings["-us_start-"] = sg.user_settings_get_entry("-us_start-", "1")
    settings["-us_step-"] = sg.user_settings_get_entry("-us_step-", "1")

def pdfin_changed(values):
    global pdfin_path
    dPrint("pdfin_changed")
    dPrint(f"values: {values}")
    pdfin_path = values["-PDFIN-"]
    dPrint(f"pdfin_path: {pdfin_path}")

def pdfin_check(window):
    global pdfin_path
    global src_pdf
    dPrint("pdfin_check")
    #Check input
    if pdfin_path == "":
        window["-SRC_SIZE-"].update("Afmetingen bron: ")
        sg.popup_error(f"Bron PDF is niet opgegeven.", title="Fout")
        return
    elif os.path.exists(pdfin_path):
        dPrint(f"File {pdfin_path} exists. OK.")
        src_pdf = fitz.open(pdfin_path)
        dPrint(f"src_pdf.name: {src_pdf.name}")
        dPrint(f"src_pdf.metadata: {src_pdf.metadata}")
        dPrint(f"src_pdf.is_pdf: {src_pdf.is_pdf}")
        if not src_pdf.is_pdf:
            sg.popup_error(f"{src_pdf.name} is geen geldig PDF bestand.", title="Fout")
            src_pdf = fitz.open(None)
        else:
            dPrint(f"Page width: {src_pdf[0].rect.width}    Page height: {src_pdf[0].rect.height}")
        window["-SRC_SIZE-"].update(f"breedte: {src_pdf[0].rect.width} px    hoogte: {src_pdf[0].rect.height} px")
        return
    else:
        window["-SRC_SIZE-"].update("Afmetingen bron: ")
        sg.popup_error(f"Bron PDF {pdfin_path} bestaat niet.", title="Fout")
        return

def logoin_changed(values):
    dPrint("logoin_changed")
    dPrint(f"values: {values}")
    settings["-us_logoin-"] = values["-LOGOIN-"]
    dPrint(f'logoin_path: {settings["-us_logoin-"]}')

def logoin_check(window):
    global settings
    global logo
    dPrint("logoin_check")
    #Check input
    if settings["-us_logoin-"] == "":
        window["-LOGO_SIZE-"].update("Originele afmetingen logo: ")
        sg.popup_error(f"Logo is niet opgegeven.", title="Fout")
        return
    elif os.path.exists(settings["-us_logoin-"]):
        dPrint(f'File {settings["-us_logoin-"]} exists. OK.')
        logo = fitz.open(settings["-us_logoin-"])
        dPrint(logo)
        dPrint(f"Logo native width: {logo[0].rect.width}    Logo native height: {logo[0].rect.height}")
        window["-LOGO_SIZE-"].update(f"Originele breedte: {logo[0].rect.width} px    hoogte: {logo[0].rect.height} px")
        sg.user_settings_set_entry("-us_logoin-", settings["-us_logoin-"])
        return
    else:
        window["-LOGO_SIZE-"].update("Originele afmetingen logo: ")
        sg.popup_error(f'Logo {settings["-us_logoin-"]} bestaat niet.', title="Fout")
        return

def position_changed(values):
    global settings
    settings["-us_logopos-"]["x1"] = intOrNone(values["-POS_X1-"])
    settings["-us_logopos-"]["y1"] = intOrNone(values["-POS_Y1-"])
    settings["-us_logopos-"]["x2"] = intOrNone(values["-POS_X2-"])
    settings["-us_logopos-"]["y2"] = intOrNone(values["-POS_Y2-"])
    sg.user_settings_set_entry("-us_logopos-", settings["-us_logopos-"])
    dPrint(f'logo position x1: {settings["-us_logopos-"]["x1"]}, y1: {settings["-us_logopos-"]["y1"]}, x2: {settings["-us_logopos-"]["x2"]}, y2: {settings["-us_logopos-"]["y2"]}')

def startstep_changed(values):
    global settings
    settings["-us_start-"] = intOrNone(values["-START-"])
    sg.user_settings_set_entry("-us_start-", settings["-us_start-"])
    settings["-us_step-"] = intOrNone(values["-STEP-"])
    sg.user_settings_set_entry("-us_step-", settings["-us_step-"])
    dPrint(f'start page: {settings["-us_start-"]} page step: {settings["-us_step-"]}')

def pdfout_changed(values):
    global pdfout_path
    pdfout_path = values["-PDFOUT-"]
    dPrint(f"pdfout_path: {pdfout_path}")

def main():
    """
    Puts a logo (PNG, JPG or PDF) over a PDF file and wtites the results as a new PDF file.
    The last chosen logo and its destination position are remembered.
    """
    getsettings()
    sg.Print(settings)

    # The window Layout
    labellength = 23
    pathlength = 80
    layout = [
        [
            sg.Text("Bron PDF", size=(labellength, 1)),
            sg.In(size=(pathlength, 1), enable_events=True, key="-PDFIN-"),
            sg.FileBrowse("Openen...", file_types=[("PDF","*.pdf")], target="-PDFIN-", key="-PDFIN_FB-")
        ],
        [
            sg.Text(" ", size=(labellength, 1)),
            sg.Button("Check bron", key="-CHK_PDFIN-"),
            sg.Text("Afmetingen bron: ", enable_events=True, key="-SRC_SIZE-")
        ],
        [
            sg.Text("Bron Logo (PNG, JPG of PDF)", size=(labellength, 1)),
            sg.In(settings["-us_logoin-"], size=(pathlength, 1), enable_events=True, key="-LOGOIN-"),
            sg.FileBrowse("Openen...", file_types=[("PNG","*.png"), ("JPG","*.jpg"), ("PDF","*.pdf")], target="-LOGOIN-", key="-LOGOIN_FB-")
        ],
        [
            sg.Text(" ", size=(labellength, 1)),
            sg.Button("Check logo", key="-CHK_LOGOIN-"),
            sg.Text("Originele afmetingen logo: ", enable_events=True, key="-LOGO_SIZE-")
        ],
        [
            sg.Text("Positie logo", size=(labellength, 1)),
            sg.Text("⟔"),
            sg.Text("x1"), sg.In(settings["-us_logopos-"]["x1"], size=(3, 1), justification="right", enable_events=True, key="-POS_X1-"),
            sg.Text("y1"), sg.In(settings["-us_logopos-"]["y1"], size=(3, 1), justification="right", enable_events=True, key="-POS_Y1-"),
            sg.Text("  ⟓"),
            sg.Text("x2"), sg.In(settings["-us_logopos-"]["x2"], size=(3, 1), justification="right", enable_events=True, key="-POS_X2-"),
            sg.Text("y2"), sg.In(settings["-us_logopos-"]["y2"], size=(3, 1), justification="right", enable_events=True, key="-POS_Y2-")
        ],
        [
            sg.Text("Op welke pagina's?", size=(labellength, 1)),
            sg.Text("1ᵉ keer op pagina"), sg.In(settings["-us_start-"], size=(3, 1), justification="center", enable_events=True, key="-START-"),
            sg.Text("daarna op elke"), sg.In(settings["-us_step-"], size=(3, 1), justification="center", enable_events=True, key="-STEP-"),
            sg.Text("pagina's (stap-waarde)")
        ],
        [
            sg.Text("Doel PDF", size=(labellength, 1)),
            sg.In(size=(pathlength, 1), enable_events=True, key="-PDFOUT-"),
            sg.FileSaveAs("Opslaan als...", target="-PDFOUT-")
        ],
        [sg.Button("Samenvoegen", key="-MERGE-")]
    ]

    window = sg.Window("PDF Logo", layout)

    # Run the Event Loop
    while True:
        event, values = window.read()
        if event in ("Exit", "Afsluiten", sg.WIN_CLOSED):
            break
        if event == "-PDFIN-":
            pdfin_changed(values)
        elif event == "-CHK_PDFIN-":
            pdfin_check(window)
        elif event == "-LOGOIN-":
            logoin_changed(values)
        elif event == "-CHK_LOGOIN-":
            logoin_check(window)
        elif event in ("-POS_X1-", "-POS_Y1-", "-POS_X2-", "-POS_Y2-"):
            position_changed(values)
        elif event in("-START-", "-STEP-"):
            startstep_changed(values)
        elif event == "-PDFOUT-":
            pdfout_changed(values)
        elif event == "-MERGE-":
            merge()

    window.close()

def intOrNone(val):
    try:
        return(int(val))
    except:
        return None

def merge():
    global pdfout_path
    global settings
    global src_pdf
    global pdfin_path
    global logo
    
    #Check input    
    if pdfout_path == "":
        sg.popup_error(f"Doel PDF is niet opgegeven", title="Fout")
        return
    else:
        pdfout_dir, pdfout_name = os.path.split(pdfout_path)
        if os.path.exists(pdfout_dir):
            pass
        else:
            sg.popup_error(f"Directory {pdfout_dir} voor {pdfout_name} bestaat niet.", title="Fout")
            return
        if os.path.exists(pdfout_path):
            sg.popup_error(f"Bestand {pdfout_path} bestaat al. Kies een andere naam.", title="Fout")
    
    if settings["-us_logopos-"]["x1"] >= settings["-us_logopos-"]["x2"]:
        sg.popup_error(f'Fout in positie:\nx1 moet kleiner zijn dan x2. x1={settings["-us_logopos-"]["x1"]}, x2={settings["-us_logopos-"]["x2"]}', title="Fout")
        return
    if settings["-us_logopos-"]["y1"] >= settings["-us_logopos-"]["y2"]:
        sg.popup_error(f'Fout in positie:\ny1 moet kleiner zijn dan y2. y1={settings["-us_logopos-"]["y1"]}, y2={settings["-us_logopos-"]["y2"]}', title="Fout")
        return
    
    if settings["-us_start-"] is None:
        sg.popup(f"Waarschuwing: Startpagina is niet opgegeven.")
        return
    if settings["-us_start-"] < 1:
        sg.popup(f"Waarschuwing: Startpagina is te klein.")
        return
    if settings["-us_step-"] is None:
        sg.popup(f"Waarschuwing: Stapwaarde pagina's is niet opgegeven.")
        return
    if settings["-us_step-"] < 1:
        sg.popup(f"Waarschuwing: Stapwaarde pagina's is te klein.")
        return
    
   
    # Open the Source PDF if not done already (Usually it is opened pressing button "-CHK_PDFIN-")
    if src_pdf.name is None:
        dPrint(f"src_pdf was not yet opened. Opening it now.")
        src_pdf = fitz.open(pdfin_path)
    dPrint(f"src_pdf opened OK.")
    numpages_pdf_in = src_pdf.page_count
    dPrint(f"{pdfin_path} has {numpages_pdf_in} pages.")

    # Put the logo on one or more pages START
    logo_rectangle = fitz.Rect(settings["-us_logopos-"]['x1'], settings["-us_logopos-"]['y1'], settings["-us_logopos-"]['x2']+1, settings["-us_logopos-"]['y2']+1) #+1 since x2,y2 by definition is *outside* the rectangle (PyMuPDF version >= 1.19.*)
    dPrint(f"logo_rectangle OK")
    
    dPrint(f"logo.name: {logo.name}")
    LogoIsPDF = None
    hf_logo_in = None
    if logo.name is None:
        # the logo is not yet opened => first try opening it as a pdf
        try:
            logo = fitz.open(settings["-us_logoin-"])
            dPrint(f'fitz.open({settings["-us_logoin-"]}) was successfull')
            if logo.is_pdf:
                LogoIsPDF = True
            else:
                LogoIsPDF = False
        except:
            dPrint(f'fitz.open({settings["-us_logoin-"]}) Failed. Will try to load it as a file stream (image?).')
            LogoIsPDF = False
    else:
        # the logo was opened using button "-CHK_LOGOIN-"
        LogoIsPDF = logo.is_pdf

    if LogoIsPDF:
        dPrint("Calling add_logo_pdf()")
        add_logo_pdf()
    else:
        dPrint("Calling add_logo_image()")
        add_logo_image()

    choice, _ = sg.Window(
        'Klaar?',
        [
            [sg.T(f"De PDF (met logo) is beschikbaar als {pdfout_path}")],
            [sg.T("Nog een PDF bewerken?")],
            [sg.Button("Ja", size=11), sg.Button("Afsluiten", size=11)]
        ],
        disable_close=True
    ).read(close=True)
    dPrint(choice)
    if choice == "Afsluiten":
        exit(0)
    
def add_logo_pdf():
    global settings
    global logo
    global src_pdf
    global pdfout_path

    numpages_pdf_in = src_pdf.page_count
    dPrint("Before the loop")
    dPrint(f'settings["-us_start-"]: {settings["-us_start-"]}')
    dPrint(f'numpages_pdf_in: {numpages_pdf_in}')
    dPrint(f'settings["-us_step-"]: {settings["-us_step-"]}')
    dPrint(f'pdfout_path: {pdfout_path}')
    for page in src_pdf.pages(settings["-us_start-"]-1, numpages_pdf_in, settings["-us_step-"]):
        dPrint(f"Doing page {page.number}")
        dPrint(f"Page height = {page.rect.height}; width = {page.rect.width}")
        # There is a bug im MuPyPDF.
        # page.show_pdf_page() does not work when _all_ parameters are named.
        # It has to have 2 or 3 positional parameters: rect, src[, pno]
        page.show_pdf_page(
            #rect=page.rect,        # Position of the logo: the entire page
            page.rect,             # Position of the logo: the entire page
            #src=doc_logopdf_in,    # the logo
            logo,                  # the logo
            pno=0,                 # Use the first (and normally only) page of the logo PDF
            clip=None,             # Don't cut out any part of the logo
            rotate=0,              # Keep the orientation of the original logo
            oc=0,                  # Don't know what this does. Doc: "control visibility via OCG / OCMD"
            keep_proportion=True,  # Keep aspect ratio of the logo
            overlay=False          # Put the logo in the background
        )
        dPrint(f"PDF Logo added to page {page.number}")
    dPrint(f"Looping over pages completed. Saving...")
    src_pdf.save(pdfout_path)
    dPrint(f"Saved OK.")

def add_logo_image():
    global settings
    global src_pdf
    global pdfout_path

    numpages_pdf_in = src_pdf.page_count
    
    dPrint("Opening the logo as a file")
    hf_logo_in = open(settings["-us_logoin-"], "rb").read()
    dPrint(f'hf_logo_in OK. metadata["format"]={logo.metadata["format"]}') #Yes, using logo, it is not a PDF, and the metadata will reflect that
    
    logo_rectangle = fitz.Rect(settings["-us_logopos-"]['x1'], settings["-us_logopos-"]['y1'], settings["-us_logopos-"]['x2']+1, settings["-us_logopos-"]['y2']+1) #+1 since x2,y2 by definition is *outside* the rectangle (PyMuPDF version >= 1.19.*)
    dPrint(f"logo_rectangle OK")

    dPrint("Before the loop")
    dPrint(f'settings["-us_start-"]: {settings["-us_start-"]}')
    dPrint(f'numpages_pdf_in: {numpages_pdf_in}')
    dPrint(f'settings["-us_step-"]: {settings["-us_step-"]}')
    dPrint(f'pdfout_path: {pdfout_path}')
    for page in src_pdf.pages(settings["-us_start-"]-1, numpages_pdf_in, settings["-us_step-"]):
        dPrint(f"Doing page {page.number}")
        dPrint(f"Page height = {page.rect.height}; width = {page.rect.width}")
        #Usign the cross reference system seems not to work: In a chromium browser, only the first page has an image.
        #In Adobe Acrobat Reader DC: "There was an error processing a page. There was a problem reading this document (18)"
        #logo_xref = 0 #images are given a cross reference in PDF, by referencing it, the same image (one binary) is used on multiple pages
        # logo_xref = page.insert_image(
        #     logo_rectangle,
        #     stream=hf_logo_in,
        #     xref=logo_xref # Reuse the image from the 2nd insertion onwards
        # )
        # Not using xref: inserting a full image on every page.
        page.insert_image(
            logo_rectangle,
            stream=hf_logo_in
        )
        dPrint(f"Image inserted on page {page.number}")
    dPrint(f"Looping over pages completed. Saving...")
    src_pdf.save(pdfout_path)
    dPrint(f"Saved OK.")



if __name__ == "__main__":
    for i, arg in enumerate(sys.argv):
        if arg=="debug":
            debug=True
    sg.user_settings_filename(path=str(Path.home())) #Write the user settings in the users home directory.
    dPrint(f"User settings stored in {str(Path.home())}")
    dPrint(fitz.__doc__)
    #sg.theme_previewer()
    main()