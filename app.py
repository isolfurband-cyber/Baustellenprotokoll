from datetime import datetime
import os
from io import BytesIO
import base64
from PIL import Image
import numpy as np
import streamlit as st
from streamlit_drawable_canvas import st_canvas
from fpdf import FPDF

st.set_page_config(
    page_title="KARE-Immobilien Handwerker- & Baustellenprotokoll",
    page_icon="🔨",
    layout="wide",
)

st.title("KARE-Immobilien – Baustellen- & Handwerkerprotokoll")
st.markdown(
    "Abnahme von Handwerkerleistungen, Baudokumentation und Erfassung von "
    "Restarbeiten oder Mängeln vor Rechnungsfreigabe."
)

with st.form("handwerker_form"):
    st.header("1. Stammdaten & Objekt")
    col1, col2 = st.columns(2)
    with col1:
        objekt_adresse = st.text_input(
            "Objektadresse / Liegenschaft", "Talstr. 32, 07545 Gera"
        )
        gewerk = st.selectbox(
            "Gewerk / Handwerksbetrieb",
            [
                "Sanitär / Heizung",
                "Elektroinstallation",
                "Maler / Tapezierer",
                "Tischler / Fenster & Türen",
                "Dachdecker / Bauklempner",
                "Fassadenbau / Wärmedämmung",
                "Bodenleger / Fliesenleger",
                "Allgemeiner Hausmeister- / Reparaturservice",
                "Sonstiges Gewerk",
            ],
        )
        handwerker_firma = st.text_input(
            "Name der Handwerksfirma / Auftragnehmer", ""
        )
    with col2:
        datum = st.date_input("Datum der Begehung / Abnahme", datetime.now())
        bearbeiter = st.text_input(
            "Abnahme durch (KARE-Immobilien)", "KARE-Immobilien"
        )
        anwesend_firma = st.text_input(
            "Anwesender Vertreter der Firma (optional)", ""
        )

    st.header("2. Leistungsumfang & Abnahmestatus")
    art_begehung = st.selectbox(
        "Art der Prüfung",
        [
            "Zwischenstand / Baustellenbegehung",
            "Mängelfeststellung",
            "Offizielle Abnahme (Werkleistung)",
            "Endabnahme nach Sanierung",
        ],
    )
    beschreibung = st.text_area(
        "Gegenstand der Arbeiten / Ausgeführte Leistungen",
        placeholder=(
            "z.B. Erneuerung der Steigleitungen im Kellergeschoss und "
            "Installation neuer Wasserzähler..."
        ),
    )

    abnahme_status = st.radio(
        "Ergebnis der Abnahme",
        [
            "Mängelfreie Abnahme (Leistung voll erbracht)",
            "Abnahme unter Vorbehalt (Mängel / Restarbeiten vorhanden)",
            "Abnahme verweigert (wesentliche Mängel)",
        ],
    )

    st.header("3. Mängel & Restarbeiten")
    maengel_text = st.text_area(
        "Festgestellte Mängel / Offene Restarbeiten (falls vorhanden)",
        placeholder=(
            "z.B. Silikonfuge im Bad beschädigt, Verkleidung sitzt nicht bündig..."
        ),
    )

    col_mass, col_frist = st.columns(2)
    with col_mass:
        massnahme = st.text_input(
            "Nacherfüllung / Vereinbarte Maßnahme",
            "Nachbesserung der aufgeführten Mängel.",
        )
    with col_frist:
        frist = st.date_input(
            "Frist zur Mängelbeseitigung", datetime.now()
        )

    st.header("4. Fotodokumentation")
    uploaded_files = st.file_uploader(
        "Fotos der Baustelle / Mängel hochladen (PNG, JPG, JPEG)",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True,
    )

    protokoll_bestätigt = st.checkbox(
        "Hiermit wird die sachliche Richtigkeit des Protokolls bestätigt."
    )

    submit_button = st.form_submit_button(
        label="Handwerkerprotokoll als PDF generieren"
    )

st.header("5. Digitale Signaturen")
col_sig_info1, col_sig_info2 = st.columns(2)
with col_sig_info1:
    st.write("**Unterschrift Handwerker / Auftragnehmer**")
    canvas_handwerker = st_canvas(
        fill_color="rgba(255, 255, 255, 0)",
        stroke_width=2,
        stroke_color="#000000",
        background_color="#ffffff",
        height=130,
        width=350,
        drawing_mode="freedraw",
        update_streamlit=True,
        return_image_data=True,
        key="canvas_handwerker_protokoll",
    )
    if canvas_handwerker.image_data is not None and np.any(canvas_handwerker.image_data[:, :, 3] > 0):
        st.session_state["saved_handwerker_sig"] = canvas_handwerker.image_data

with col_sig_info2:
    st.write("**Unterschrift KARE-Immobilien**")
    canvas_kare = st_canvas(
        fill_color="rgba(255, 255, 255, 0)",
        stroke_width=2,
        stroke_color="#000000",
        background_color="#ffffff",
        height=130,
        width=350,
        drawing_mode="freedraw",
        update_streamlit=True,
        return_image_data=True,
        key="canvas_kare_handwerker",
    )
    if canvas_kare.image_data is not None and np.any(canvas_kare.image_data[:, :, 3] > 0):
        st.session_state["saved_kare_sig"] = canvas_kare.image_data

if submit_button:
    if not protokoll_bestätigt:
        st.error(
            "Bitte bestätige das Protokoll über die Checkbox, bevor du das PDF "
            "generierst."
        )
    else:
        # FPDF PDF-Klasse definieren
        class PDF(FPDF):
            def header(self):
                self.set_font('helvetica', 'B', 16)
                self.set_text_color(2, 132, 199)
                self.cell(0, 8, "KARE-Immobilien", ln=True)
                self.set_font('helvetica', '', 9)
                self.set_text_color(85, 85, 85)
                self.cell(0, 5, "Talstr. 32, 07545 Gera | Tel.: 0365 / 800 49 37 | E-Mail: Info@KARE-Immobilien.de", ln=True)
                self.ln(4)
                self.set_draw_color(2, 132, 199)
                self.set_line_width(0.8)
                self.line(10, self.get_y(), 200, self.get_y())
                self.ln(6)

            def footer(self):
                self.set_y(-15)
                self.set_font('helvetica', '', 8)
                self.set_text_color(100, 100, 100)
                self.cell(0, 10, f"KARE-Immobilien · Talstr. 32 · 07545 Gera                Seite {self.page_no()}/{{nb}}", 0, 0, 'R')

        pdf = PDF()
        pdf.alias_nb_pages()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        # Titel des Dokuments
        pdf.set_font('helvetica', 'B', 13)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(0, 8, "Baustellen- und Handwerkerprotokoll", ln=True)
        pdf.ln(2)

        # Hilfsfunktion für Tabellenzeilen (Umlaut-Bereinigung für Standard-Helvetica)
        def clean(text):
            if not text:
                return ""
            return str(text).encode('latin-1', 'replace').decode('latin-1')

        def add_row(label, value):
            pdf.set_font('helvetica', 'B', 9)
            pdf.set_fill_color(240, 249, 255)
            pdf.set_text_color(3, 105, 161)
            pdf.cell(50, 7, clean(label), border=1, fill=True)
            pdf.set_font('helvetica', '', 9)
            pdf.set_text_color(51, 51, 51)
            pdf.cell(140, 7, clean(value), border=1, ln=True)

        # 1. Stammdaten & Objekt
        pdf.set_font('helvetica', 'B', 11)
        pdf.set_text_color(2, 132, 199)
        pdf.cell(0, 8, "1. Stammdaten & Objekt", ln=True)
        
        add_row("Objektadresse", objekt_adresse)
        add_row("Gewerk", gewerk)
        add_row("Handwerksfirma", f"{handwerker_firma} (Vertreter: {anwesend_firma})")
        add_row("Datum & Art", f"{datum.strftime('%d.%m.%Y')} - {art_begehung}")
        add_row("Abnahme durch", bearbeiter)
        pdf.ln(4)

        # 2. Leistung & Abnahmestatus
        pdf.set_font('helvetica', 'B', 11)
        pdf.set_text_color(2, 132, 199)
        pdf.cell(0, 8, "2. Leistung & Abnahmestatus", ln=True)

        add_row("Leistungsbeschreibung", beschreibung)
        add_row("Abnahmeergebnis", abnahme_status)
        add_row("Maengel / Restarbeiten", maengel_text if maengel_text else "Keine Maengel festgestellt.")
        add_row("Vereinbarte Massnahme", massnahme)
        add_row("Frist zur Mängelbeseitigung", frist.strftime('%d.%m.%Y'))
        pdf.ln(6)

        # 4. Fotodokumentation einbetten (falls vorhanden)
        if uploaded_files:
            pdf.set_font('helvetica', 'B', 11)
            pdf.set_text_color(2, 132, 199)
            pdf.cell(0, 8, "Fotodokumentation", ln=True)
            pdf.ln(2)

            for idx, file in enumerate(uploaded_files):
                img = Image.open(file)
                if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
                    img = img.convert("RGB")
                
                # Bild temporär im Arbeitsspeicher sichern
                img_path = f"temp_photo_{idx}.jpg"
                img.save(img_path, "JPEG")
                
                pdf.image(img_path, w=80)
                pdf.set_font('helvetica', '', 8)
                pdf.set_text_color(100, 100, 100)
                pdf.cell(0, 6, clean(f"Foto {idx+1}: {file.name}"), ln=True)
                pdf.ln(4)
                
                # Aufräumen
                if os.path.exists(img_path):
                    os.remove(img_path)

        # Signaturen verarbeiten und einfügen
        pdf.ln(5)
        pdf.set_font('helvetica', 'B', 11)
        pdf.set_text_color(2, 132, 199)
        pdf.cell(0, 8, "Unterschriften", ln=True)
        pdf.ln(2)

        def save_sig_to_file(state_key, filename):
            if state_key in st.session_state and st.session_state[state_key] is not None:
                img_data = st.session_state[state_key].astype("uint8")
                pil_img = Image.fromarray(img_data, mode="RGBA")
                background = Image.new("RGB", pil_img.size, (255, 255, 255))
                background.paste(pil_img, mask=pil_img.split()[3])
                background.save(filename, "PNG")
                return True
            return False

        sig1_exists = save_sig_to_file("saved_handwerker_sig", "sig1.png")
        sig2_exists = save_sig_to_file("saved_kare_sig", "sig2.png")

        start_y = pdf.get_y()
        
        # Handwerker Unterschrift Block
        pdf.set_xy(10, start_y)
        if sig1_exists:
            pdf.image("sig1.png", w=60)
            pdf.ln(2)
        else:
            pdf.ln(15)
        pdf.set_x(10)
        pdf.set_font('helvetica', '', 9)
        pdf.set_text_color(51, 51, 51)
        pdf.cell(90, 5, "____________________________________", ln=True)
        pdf.set_x(10)
        pdf.cell(90, 5, clean("Handwerker / Auftragnehmer"))

        # KARE-Immobilien Unterschrift Block
        pdf.set_xy(110, start_y)
        if sig2_exists:
            pdf.image("sig2.png", w=60)
            pdf.ln(2)
        else:
            pdf.ln(15)
        pdf.set_x(110)
        pdf.cell(90, 5, "____________________________________", ln=True)
        pdf.set_x(110)
        pdf.cell(90, 5, clean("KARE-Immobilien"))

        # Temporäre Signatur-Dateien aufräumen
        for f in ["sig1.png", "sig2.png"]:
            if os.path.exists(f):
                os.remove(f)

        pdf_bytes = pdf.output(dest='S').encode('latin1')

        st.success("Handwerkerprotokoll erfolgreich als PDF erstellt!")
        st.download_button(
            label="📄 Handwerkerprotokoll als PDF herunterladen",
            data=pdf_bytes,
            file_name=(
                f"Handwerker_{datum.strftime('%Y%m%d')}_{gewerk.split('/')[0].strip()}.pdf"
            ),
            mime="application/pdf",
        )
