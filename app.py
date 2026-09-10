from datetime import datetime
import io
from fpdf import FPDF
from PIL import Image
import streamlit as st
from streamlit_drawable_canvas import st_canvas

# Seitenkonfiguration
st.set_page_config(
    page_title="KARE-Immobilien - Baustellenprotokoll",
    page_icon="🏗️",
    layout="wide",
)

# -------------------------------------------------------------
# FPDF KLASSE MIT HEADER & FOOTER
# -------------------------------------------------------------


class PDFProtocol(FPDF):

  def __init__(self, protocol_type="Baustellenprotokoll"):
    super().__init__()
    self.protocol_type = protocol_type

  def header(self):
    self.set_font("Helvetica", "B", 14)
    self.set_text_color(20, 40, 80)
    self.cell(
        0, 8, "KARE-Immobilien - Baustellenprotokoll", 0, 1, "LEFT"
    )

    self.set_font("Helvetica", "", 9)
    self.set_text_color(100, 100, 100)
    self.cell(
        0,
        5,
        "Talstr. 32 | 07545 Gera | Tel.: 0365 / 800 49 37 | E-Mail: Info@KARE-Immobilien.de",
        0,
        1,
        "LEFT",
    )
    self.ln(3)

    self.set_draw_color(200, 200, 200)
    self.set_line_width(0.4)
    self.line(10, self.get_y(), 200, self.get_y())
    self.ln(5)

  def footer(self):
    self.set_y(-15)
    self.set_font("Helvetica", "I", 8)
    self.set_text_color(120, 120, 120)
    self.cell(
        0,
        10,
        f"Seite {self.page_no()} von {{nb}} | KARE-Immobilien - Baustellenprotokoll",
        0,
        0,
        "C",
    )


# -------------------------------------------------------------
# STREAMLIT BENUTZEROBERFLÄCHE
# -------------------------------------------------------------

st.title("🏗️ KARE-Immobilien – Digitales Baustellenprotokoll")
st.markdown(
    "Erstellen Sie hier Ihr Protokoll für Baustellen und Handwerkerleistungen."
)

with st.form("protocol_form"):
  st.subheader("1. Objektdaten & Firma")
  col1, col2 = st.columns(2)
  with col1:
    ort = st.text_input("Ort / Baustelle / Adresse", "Talstr. 32, 07545 Gera")
    firma = st.text_input(
        "Auszuführende Firma / Gewerk", "Muster-Handwerksfirma GmbH"
    )
  with col2:
    date = st.date_input("Datum der Begehung", datetime.now())
    bearbeiter = st.text_input("Protokoll geführt durch", "KARE-Immobilien")

  st.divider()

  st.subheader("2. Mängel & Feststellungen")
  maengel = st.text_area(
      "Beschreibung der Mängel / Aufgaben / Feststellungen",
      placeholder="z.B. Malerarbeiten im Flur unvollständig, Steckdose lose...",
      height=150,
  )

  st.divider()

  st.subheader("3. Fotodokumentation")
  uploaded_files = st.file_uploader(
      "Bilder hochladen (PNG, JPG, JPEG)",
      type=["png", "jpg", "jpeg"],
      accept_multiple_files=True,
  )

  st.divider()

  st.subheader("4. Digitale Unterschriften")
  col_sig1, col_sig2 = st.columns(2)
  with col_sig1:
    st.markdown("**Unterschrift Auftraggeber (KARE)**")
    canvas_client = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",
        stroke_width=2,
        stroke_color="#000000",
        background_color="#FFFFFF",
        height=120,
        width=300,
        drawing_mode="freedraw",
        return_image_data=True,
        key="canvas_client",
    )

  with col_sig2:
    st.markdown("**Unterschrift Ausführende Firma / Vertreter**")
    canvas_contractor = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",
        stroke_width=2,
        stroke_color="#000000",
        background_color="#FFFFFF",
        height=120,
        width=300,
        drawing_mode="freedraw",
        return_image_data=True,
        key="canvas_contractor",
    )

  submitted = st.form_submit_button(
      "Protokoll als PDF generieren & herunterladen"
  )

# -------------------------------------------------------------
# PDF GENERIERUNGS-LOGIK
# -------------------------------------------------------------

if submitted:
  pdf = PDFProtocol()
  pdf.alias_nb_pages()
  pdf.add_page()
  pdf.set_auto_page_break(auto=True, margin=15)

  # Titel des Dokuments
  pdf.set_font("Helvetica", "B", 16)
  pdf.set_text_color(20, 40, 80)
  pdf.cell(0, 10, "Baustellenprotokoll", 0, 1, "C")
  pdf.ln(5)

  # Objektdaten-Box
  pdf.set_font("Helvetica", "B", 10)
  pdf.set_fill_color(240, 244, 248)
  pdf.cell(0, 7, " Baustellendaten", 0, 1, "L", fill=True)

  pdf.set_font("Helvetica", "", 10)
  pdf.set_text_color(50, 50, 50)

  col_w1, col_w2 = 95, 95
  pdf.cell(col_w1, 6, f" Ort / Baustelle: {ort}", 0, 0, "L")
  pdf.cell(col_w2, 6, f" Datum: {date.strftime('%d.%m.%Y')}", 0, 1, "L")
  pdf.cell(col_w1, 6, f" Auszuführende Firma: {firma}", 0, 0, "L")
  pdf.cell(col_w2, 6, f" Protokoll durch: {bearbeiter}", 0, 1, "L")
  pdf.ln(5)

  # Mängel / Feststellungen
  pdf.set_font("Helvetica", "B", 10)
  pdf.set_fill_color(240, 244, 248)
  pdf.cell(0, 7, " Mängel & Feststellungen", 0, 1, "L", fill=True)
  pdf.ln(2)
  pdf.set_font("Helvetica", "", 10)
  pdf.multi_cell(
      0,
      6,
      maengel
      if maengel.strip()
      else "Keine Mängel / Feststellungen eingetragen.",
  )
  pdf.ln(5)

  # Fotodokumentation im PDF einbetten
  if uploaded_files:
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_fill_color(240, 244, 248)
    pdf.cell(0, 7, " Fotodokumentation", 0, 1, "L", fill=True)
    pdf.ln(3)

    for idx, uploaded_file in enumerate(uploaded_files):
      try:
        image = Image.open(uploaded_file)
        if image.mode in ("RGBA", "LA"):
          image = image.convert("RGB")

        img_io = io.BytesIO()
        image.save(img_io, format="JPEG", quality=85)
        img_io.seek(0)

        if pdf.get_y() > 210:
          pdf.add_page()

        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(0, 6, f"Foto {idx+1}: {uploaded_file.name}", 0, 1, "L")
        pdf.image(img_io, w=100)
        pdf.ln(5)
      except Exception as e:
        print(f"Fehler beim Einbinden des Bildes: {e}")

  # Unterschriften Sektion
  if pdf.get_y() > 220:
    pdf.add_page()

  pdf.set_font("Helvetica", "B", 10)
  pdf.set_fill_color(240, 244, 248)
  pdf.cell(0, 7, " Unterschriften", 0, 1, "L", fill=True)
  pdf.ln(5)

  y_img_canv = pdf.get_y()

  pdf.set_font("Helvetica", "B", 9)
  pdf.cell(95, 5, "Unterschrift Auftraggeber", 0, 0, "L")
  pdf.cell(95, 5, "Unterschrift Ausführende Firma", 0, 1, "L")

  def embed_signature(canvas_obj, x_pos):
    if canvas_obj.image_data is not None:
      try:
        img = Image.fromarray(
            canvas_obj.image_data.astype("uint8"), mode="RGBA"
        )
        img_io = io.BytesIO()
        img.save(img_io, format="PNG")
        img_io.seek(0)
        pdf.image(img_io, x=x_pos, y=y_img_canv + 5, w=85)
      except Exception as e:
        print(f"Fehler beim Laden der Unterschrift: {e}")

  embed_signature(canvas_client, 10)
  embed_signature(canvas_contractor, 110)

  pdf.ln(25)
  pdf.set_font("Helvetica", "I", 8)
  pdf.set_text_color(100, 100, 100)
  pdf.cell(
      0,
      6,
      "Ort, Datum, Unterschriften bestätigen die Richtigkeit der obigen Angaben.",
      0,
      1,
      "L",
  )

  pdf_bytes = bytes(pdf.output())

  st.success("Baustellenprotokoll wurde erfolgreich erstellt!")
  st.download_button(
      label="📥 PDF-Protokoll herunterladen",
      data=pdf_bytes,
      file_name=(
          f"Baustellenprotokoll_{firma.replace(' ', '_')}_{date.strftime('%Y%m%d')}.pdf"
      ),
      mime="application/pdf",
  )
