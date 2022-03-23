# pdflogo.pyw

from tkinter import NONE #Use wrapper PySimpleGUI instead
import PySimpleGUI as sg

import fitz #a.k.a. PyMuPDF, to work with PDFs

import os.path
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

def main():
    """
    Puts a logo (PNG, JPG or PDF) over a PDF file and wtites the results as a new PDF file.
    The last chosen logo and its destination position are remembered.
    """
    # Initiate the PDF paths (PDF in and out)
    pdfin_path = ""
    pdfout_path = ""
    # Try to get the last used logo from the user settings
    logoin_path = sg.user_settings_get_entry("-us_logoin-", "")
    # Try to get the last used logo position from the user settings
    position = sg.user_settings_get_entry("-us_logopos-",
        {"x1": None, "y1": None, "x2": None, "y2": None})
    # try to get the last start and step page indicators from the user settings
    start_str = sg.user_settings_get_entry("-us_start-", "1")
    dPrint(f"from user settings, start_str={start_str}")
    start = intOrNone(start_str) #needed in order to have it as parameter of merge()
    dPrint(f"from user settings, start={start}")
    step_str = sg.user_settings_get_entry("-us_step-", "1")
    dPrint(f"from user settings, step_str={step_str}")
    step = intOrNone(step_str)   #needed in order to have it as parameter of merge()
    dPrint(f"from user settings, step={step}")

    # The window Layout
    labellength = 23
    pathlength = 80
    layout = [
        [
            sg.Text("Bron PDF", size=(labellength, 1)),
            sg.In(size=(pathlength, 1), enable_events=True, key="-PDFIN-"),
            sg.FileBrowse("Openen...", target="-PDFIN-")
        ],
        [
            sg.Text()
        ],
        [
            sg.Text("Bron Logo (PNG, JPG of PDF)", size=(labellength, 1)),
            sg.In(logoin_path, size=(pathlength, 1), enable_events=True, key="-LOGOIN-"),
            sg.FileBrowse("Openen...", target="-LOGOIN-")
        ],
        [
            sg.Text("Positie logo", size=(labellength, 1)),
            sg.Text("⟔"),
            sg.Text("x1"), sg.In(position["x1"], size=(3, 1), justification="right", enable_events=True, key="-POS_X1-"),
            sg.Text("y1"), sg.In(position["y1"], size=(3, 1), justification="right", enable_events=True, key="-POS_Y1-"),
            sg.Text("⟓"),
            sg.Text("x2"), sg.In(position["x2"], size=(3, 1), justification="right", enable_events=True, key="-POS_X2-"),
            sg.Text("y2"), sg.In(position["y2"], size=(3, 1), justification="right", enable_events=True, key="-POS_Y2-"),
            sg.Text("A4: breedte (x) = 612   hoogte (y) = 792")
        ],
        [
            sg.Text("Op welke pagina's?", size=(labellength, 1)),
            sg.Text("1ᵉ keer op pagina"), sg.In(start_str, size=(3, 1), justification="center", enable_events=True, key="-START-"),
            sg.Text("daarna op elke"), sg.In(step_str, size=(3, 1), justification="center", enable_events=True, key="-STEP-"),
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
            pdfin_path = values["-PDFIN-"]
        elif event == "-LOGOIN-":
            logoin_path = values["-LOGOIN-"]
            sg.user_settings_set_entry("-us_logoin-", logoin_path)
        elif event == "-PDFOUT-":
            pdfout_path = values["-PDFOUT-"]
        elif event in ("-POS_X1-", "-POS_Y1-", "-POS_X2-", "-POS_Y2-"):
            position["x1"] = intOrNone(values["-POS_X1-"])
            position["y1"] = intOrNone(values["-POS_Y1-"])
            position["x2"] = intOrNone(values["-POS_X2-"])
            position["y2"] = intOrNone(values["-POS_Y2-"])
            sg.user_settings_set_entry("-us_logopos-", position)
        elif event in("-START-", "-STEP-"):
            start = intOrNone(values["-START-"])
            sg.user_settings_set_entry("-us_start-", values["-START-"])
            step = intOrNone(values["-STEP-"])
            sg.user_settings_set_entry("-us_step-", values["-STEP-"])
            dPrint(f"In event loop:")
            dPrint(f'    start_str={sg.user_settings_get_entry("-us_start-", "-99")}')
            dPrint(f"    start    ={start}")
            dPrint(f'    step_str ={sg.user_settings_get_entry("-us_step-", "-99")}')
            dPrint(f"    step     ={step}")
        elif event == "-MERGE-":
            merge(pdfin_path, logoin_path, pdfout_path, position, start, step)

    window.close()

def intOrNone(val):
    try:
        return(int(val))
    except:
        return None

def merge(pdfin_path, logoin_path, pdfout_path, position, start, step):
    dPrint(f"(Before testing) PDF IN: {pdfin_path}\nLOGO IN: {logoin_path}\nPDF OUT: {pdfout_path}")
    
    #Check input
    if pdfin_path == "":
        sg.popup_error(f"Bron PDF is niet opgegeven.", title="Fout")
        return
    elif os.path.exists(pdfin_path):
        pass
    else:
        sg.popup_error(f"Bron PDF {pdfin_path} bestaat niet.", title="Fout")
        return
    
    if logoin_path == "":
        sg.popup_error(f"Logo is niet opgegeven.", title="Fout")
        return
    elif os.path.exists(logoin_path):
        pass
    else:
        sg.popup_error(f"Logo {logoin_path} bestaat niet.", title="Fout")
        return
    
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
    
    if position["x1"] >= position["x2"]:
        sg.popup_error(f"Fout in positie:\nx1 moet kleiner zijn dan x2. x1={position['x1']}, x2={position['x2']}", title="Fout")
        return
    if position["y1"] >= position["y2"]:
        sg.popup_error(f"Fout in positie:\ny1 moet kleiner zijn dan y2. y1={position['y1']}, y2={position['y2']}", title="Fout")
        return
    
    if start is None:
        sg.popup(f"Waarschuwing: Startpagina is niet opgegeven.")
        return
    if start < 1:
        sg.popup(f"Waarschuwing: Startpagina is te klein.")
        return
    if step is None:
        sg.popup(f"Waarschuwing: Stapwaarde pagina's is niet opgegeven.")
        return
    if step < 1:
        sg.popup(f"Waarschuwing: Stapwaarde pagina's is te klein.")
        return
    
    dPrint(f"(After testing) PDF IN: {pdfin_path}\nLOGO IN: {logoin_path}\nPDF OUT: {pdfout_path}")
   
    
    #####
    # Put the logo on one or more pages START
    hf_pdf_in = fitz.open(pdfin_path)
    dPrint(f"hf_pdf_in OK.")
    numpages_pdf_in = hf_pdf_in.page_count
    dPrint(f"{pdfin_path} has {numpages_pdf_in} pages.")
    logo_rectangle = fitz.Rect(position['x1'], position['y1'], position['x2']+1, position['y2']+1) #+1 since x2,y2 by definition is outside the rectangle (PyMuPDF version >= 1.19.*)
    dPrint(f"logo_rectangle OK")
    hf_logo_in = open(logoin_path, "rb").read()
    try:
        doc_logopdf_in = fitz.open(logoin_path)
        dPrint(f"fitz.open({logoin_path}) was successfull")
    except:
        dPrint(f"fitz.open({logoin_path}) Failed. Using an empty document as a logo.")
        doc_logopdf_in = fitz.open(None)
    dPrint(f'hf_logo_in OK. metadata["format"]={doc_logopdf_in.metadata["format"]}')
    LogoIsPDF = doc_logopdf_in.metadata["format"][0:3] == "PDF"

    for page in hf_pdf_in.pages(start-1, numpages_pdf_in, step):
        dPrint(f"Doing page {page.number}")
        dPrint(f"Page height = {page.rect.height}; width = {page.rect.width}")
        if LogoIsPDF:
            # There is a bug im MuPyPDF.
            # page.show_pdf_page() does not work when all parameters are named.
            # It has to have 2 or 3 positional parameters: rect, src[, pno]
            # The documentaiton is also not very clear regarding the pno variable:
            #    it is the pagenumber in the _src_ PDF, not the one from which _page_ is (which makes sence, really)
            page.show_pdf_page(
                #rect=page.rect,        # Position of the logo: the entire page
                page.rect,             # Position of the logo: the entire page
                #src=doc_logopdf_in,    # the logo
                doc_logopdf_in,        # the logo
                pno=0,                 # Use the first (and normally only) page of the loge PDF
                clip=None,             # Don't cut out any part of the logo
                rotate=0,              # Keep the orientation of the original logo
                oc=0,                  # Don't know what this does. Doc: "control visibility via OCG / OCMD"
                keep_proportion=True,  # Keep aspect ratio of the logo
                overlay=False          # Put the logo in the background
            )
            dPrint("PDF Logo added")
        else: #Logo is not a PDF, so hopefully an image
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
            dPrint("Image inserted")

    dPrint(f"looping over pages completed")
    hf_pdf_in.save(pdfout_path)
    dPrint(f"Saved OK.")

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
    



if __name__ == "__main__":
    for i, arg in enumerate(sys.argv):
        if arg=="debug":
            debug=True
    sg.user_settings_filename(path=".") #Write the user settings in the local directory.
    dPrint(fitz.__doc__)
    #sg.theme_previewer()
    main()