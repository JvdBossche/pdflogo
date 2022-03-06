# pdflogo.py

from tkinter import NONE #Use wrapper PySimpleGUI instead
import PySimpleGUI as sg
import os.path
import fitz #a.k.a. PyMuPDF, to import a PNG in a PDF

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
    step_str = sg.user_settings_get_entry("-us_step-", "1")

    # The window Layout
    labellength = 23
    pathlength = 80
    layout = [
        [
            sg.Text("Bron PDF", size=(labellength, 1)),
            sg.In(size=(pathlength, 1), enable_events=True, key="-PDFIN-"),
            sg.FileBrowse()
        ],
        [
            sg.Text("Bron Logo (PNG, JPG of PDF)", size=(labellength, 1)),
            sg.In(logoin_path, size=(pathlength, 1), enable_events=True, key="-LOGOIN-"),
            sg.FileBrowse()
        ],
        [
            sg.Text("Positie logo", size=(labellength, 1)),
            sg.Text("x1"), sg.In(position["x1"], size=(3, 1), justification="right", enable_events=True, key="-POS_X1-"),
            sg.Text("y1"), sg.In(position["y1"], size=(3, 1), justification="right", enable_events=True, key="-POS_Y1-"),
            sg.Text("x2"), sg.In(position["x2"], size=(3, 1), justification="right", enable_events=True, key="-POS_X2-"),
            sg.Text("y2"), sg.In(position["y2"], size=(3, 1), justification="right", enable_events=True, key="-POS_Y2-")
        ],
        [
            sg.Text("Op welke pagina's?", size=(labellength, 1)),
            sg.Text("1ᵉ pagina"), sg.In(start_str, size=(3, 1), justification="right", enable_events=True, key="-START-"),
            sg.Text("Herhalen elke"), sg.In(step_str, size=(3, 1), justification="right", enable_events=True, key="-STEP-"),
            sg.Text("pagina's (stap-waarde)")
        ],
        [
            sg.Text("Doel PDF", size=(labellength, 1)),
            sg.In(size=(pathlength, 1), enable_events=True, key="-PDFOUT-"),
            sg.FileSaveAs()
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
            if start is not None:
                sg.user_settings_set_entry("-us_start-", values["-START-"])
                start = start - 1 #PyMuPDF uses pagenumbering starting from 0!
            step = intOrNone(values["-STEP-"])
            sg.user_settings_set_entry("-us_step-", values["-STEP-"])
        elif event == "-MERGE-":
            merge(pdfin_path, logoin_path, pdfout_path, position, start, step)

    window.close()

def intOrNone(val):
    try:
        return(int(val))
    except:
        return None

def merge(pdfin_path, logoin_path, pdfout_path, position, start, step):
    sg.Print(f"(Before testing) PDF IN: {pdfin_path}\nLOGO IN: {logoin_path}\nPDF OUT: {pdfout_path}")
    
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
    
    if start < 0:
        sg.popup(f"Waarschuwing: Startpagina is negatief.")
        return
    if step < 0:
        sg.popup(f"Waarschuwing: Stapwaarde pagina's is negatief.")
        return
    
    sg.Print(f"(After testing) PDF IN: {pdfin_path}\nLOGO IN: {logoin_path}\nPDF OUT: {pdfout_path}")
   
    
    #####
    # Put the logo on one or more pages START
    hf_pdf_in = fitz.open(pdfin_path)
    sg.Print(f"hf_pdf_in OK.")
    numpages_pdf_in = hf_pdf_in.page_count
    sg.Print(f"{pdfin_path} has {numpages_pdf_in} pages.")
    logo_rectangle = fitz.Rect(position['x1'], position['y1'], position['x2'], position['y2'])
    sg.Print(f"logo_rectangle OK")
    hf_logo_in = open(logoin_path, "rb").read()
    try:
        doc_logopdf_in = fitz.open(logoin_path)
    except:
        doc_logopdf_in = fitz.open(None)
    sg.Print(f"hf_logo_in OK")
    #Usign the cross reference system seems not to work: In a chromium browser, only the first page has an image.
    #In Adobe Acrobat Reader DC: "There was an error processing a page. There was a problem reading this document (18)"
    #logo_xref = 0 #images are given a cross reference in PDF, by referencing it, the same image (one binary) is used on multiple pages
    #sg.Print(f"logo_xref OK. xref={logo_xref}")
    #start = 0 # Put images, starting from the first page
    #step = 2  # Put images on alternating pages
    for page in hf_pdf_in.pages(start, numpages_pdf_in, step):
        sg.Print(f"Doing page {page.number}")
        # logo_xref = page.insert_image(
        #     logo_rectangle,
        #     stream=hf_logo_in,
        #     xref=logo_xref #reuse the image from the 2nd insertion
        # )
        # Not using xref: inserting a full image on every page.
        try:
            page.insert_image(
                logo_rectangle,
                stream=hf_logo_in
            )
            sg.Print("Image inserted")
        except:
            sg.Print("Image failed, trying pdf")
            page.show_pdf_page(
                rect=logo_rectangle,
                src=doc_logopdf_in,
                overlay=True
            )
            # try:
            #     page.show_pdf_page(
            #         logo_rectangle,
            #         src=doc_logopdf_in,
            #         overlay=True
            #     )
            #     sg.Print("PDF inserted")
            # except:
            #     sg.Print(f"ERROR: Fialed to insert {logoin_path}")
        #sg.Print(f"xref={logo_xref}")
    sg.Print(f"looping over pages completed")
    hf_pdf_in.save(pdfout_path)
    sg.Print(f"Saved OK.")
    # Put the logo on one or more pages END
    #####
    choice, _ = sg.Window(
        'Klaar?',
        [
            [sg.T(f"De PDF (met logo) is beschikbaar als {pdfout_path}")],
            [sg.T("Nog een PDF bewerken?")],
            [sg.Button("Ja", size=11), sg.Button("Afsluiten", size=11)]
        ],
        disable_close=True
    ).read(close=True)
    sg.Print(choice)
    if choice == "Afsluiten":
        exit(0)
    



if __name__ == "__main__":
    sg.user_settings_filename(path=".") #Write the user settings in the local directory.
    sg.Print(fitz.__doc__)
    main()