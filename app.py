from datetime import datetime
import io
from fpdf import FPDF
from PIL import Image
import streamlit as st
from streamlit_drawable_canvas import st_canvas

# Seitenkonfiguration
st.set_page_config(
    page_title="KARE-Immobilien – Wohnungsabnahmeprotokoll",
    page_icon="📋",
    layout="wide",
)

# -------------------------------------------------------------
# FPDF KLASSE MIT HEADER & FOOTER
# -------------------------------------------------------------


class PDFProtocol(FPDF):

  def __init__(self, protocol_type="Übergabe"):
    super().__init__()
    self.protocol_type = protocol_type

  def header(self):
    # Firmenkopf
    self.set_font("Helvetica", "B", 14)
    self.set_text_color(20, 40, 80)
    self.cell(
        0, 8, "KARE-Immobilien – Wohnungsabnahmeprotokoll", 0, 1, "LEFT"
    )

    self.set_font("Helvetica", "", 9)
    self.set_text_color(100, 100, 100)
    self.cell(
        0,
        5,
        "Talstr. 32 | 07545 Gera | Tel.: 0365 / 800 49 37 | E-Mail:"
        " Info@KARE-Immobilien.de",
        0,
        1,
        "LEFT",
    )
    self.ln(3)

    # Trennlinie
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
        f"Seite {self.page_no()} von {{nb}} | KARE-Immobilien - Protokoll"
        f" ({self.protocol_type})",
        0,
        0,
        "C",
    )


# -------------------------------------------------------------
# STREAMLIT BENUTZEROBERFLÄCHE
# -------------------------------------------------------------

st.title("📋 KARE-Immobilien – Digitales Abnahmeprotokoll")
st.markdown(
    "Erstellen Sie hier das rechtssichere Wohnungsabnahmeprotokoll für Ihre"
    " Mietobjekte in Gera."
)

with st.form("protocol_form"):
  st.subheader("1. Allgemeine Objektdaten")
  col1, col2 = st.columns(2)
  with col1:
    proto_type = st.selectbox(
        "Protokoll-Art", ["Wohnungsübergabe", "Wohnungsrückgabe"]
    )
    street = st.text_input("Straße & Hausnummer", "Talstr. 32")
    zip_city = st.text_input("PLZ & Ort", "07545 Gera")
    floor = st.text_input("Etage / Lage", "2. Obergeschoss links")
  with col2:
    date = st.date_input("Datum der Abnahme", datetime.now())
    landlord = st.text_input(
        "Vermieter / Vertreter", "KARE-Immobilien (Hausverwaltung)"
    )
    tenant = st.text_input("Mieter", "Max Mustermann")
    keys_handed = st.text_input(
        "Übergebene Schlüssel (Anzahl & Art)",
        "3x Wohnungsschlüssel, 2x Kellerschlüssel, 1x Briefkastenschlüssel",
    )

  st.divider()

  st.subheader("2. Zählerstände")
  st.markdown(
      "Bitte tragen Sie die aktuellen Zählerstände und Zählernummern ein:"
  )

  col_z1, col_z2 = st.columns(2)
  with col_z1:
    kw_num = st.text_input("Zählernummer Kaltwasser", "KW-987654")
    kw_val = st.text_input("Stand Kaltwasser (m³)", "142.50")
    ww_num = st.text_input("Zählernummer Warmwasser", "WW-123456")
    ww_val = st.text_input("Stand Warmwasser (m³)", "58.20")
  with col_z2:
    st.markdown("##### Heizungszähler (Heizkostenverteiler)")
    h_wz = st.text_input("Wohnzimmer (Nr. / Stand)", "HZ-01: 1245")
    h_kz = st.text_input("Kinderzimmer (Nr. / Stand)", "HZ-02: 832")
    h_fl = st.text_input("Flur (Nr. / Stand)", "HZ-03: 150")
    h_ba = st.text_input("Bad (Nr. / Stand)", "HZ-04: 610")
    h_ku = st.text_input("Küche (Nr. / Stand)", "HZ-05: 445")

  st.divider()

  st.subheader("3. Mängel & Zustand der Räume")
  rooms = ["Wohnzimmer", "Kinderzimmer", "Flur", "Bad", "Küche", "Schlafzimmer"]
  room_data = {}

  for room in rooms:
    with st.expander(f"Raum: {room}"):
      c1, c2 = st.columns(2)
      with c1:
        cond = st.selectbox(
            f"Zustand {room}", ["Einwandfrei", "Gebrauchsspuren", "Mängel"], key=f"c_{room}"
        )
      with c2:
        defects = st.text_area(
            f"Mängel / Bemerkungen in {room}",
            placeholder="z.B. Bohrlocher in Wand, leichte Kratzer Parkett...",
            key=f"d_{room}",
        )
      room_data[room] = {"zustand": cond, "maengel": defects}

  st.divider()

  st.subheader("4. Allgemeine Vereinbarungen & Nacharbeiten")
  agreements = st.text_area(
      "Vereinbarte Fristen oder Sonderabsprachen",
      placeholder=(
          "z.B. Mieter streicht das Schlafzimmer bis zum 30.09. fachgerecht"
          " nach..."
      ),
  )

  st.divider()

  st.subheader("5. Digitale Unterschriften")
  st.markdown("Bitte unterschreiben Sie im Feld unten:")

  col_sig1, col_sig2 = st.columns(2)
  with col_sig1:
    st.markdown("**Unterschrift Vermieter / Vertreter**")
    canvas_landlord = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",
        stroke_width=2,
        stroke_color="#000000",
        background_color="#FFFFFF",
        height=150,
        width=350,
        drawing_mode="freedraw",
        key="canvas_landlord",
    )

  with col_sig2:
    st.markdown("**Unterschrift Mieter**")
    canvas_tenant = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",
        stroke_width=2,
        stroke_color="#000000",
        background_color="#FFFFFF",
        height=150,
        width=350,
        drawing_mode="freedraw",
        key="canvas_tenant",
    )

  submitted = st.form_submit_button(
      "Protokoll als PDF generieren & herunterladen"
  )

# -------------------------------------------------------------
# PDF GENERIERUNGS-LOGIK
# -------------------------------------------------------------

if submitted:
  pdf = PDFProtocol(protocol_type=proto_type)
  pdf.alias_nb_pages()
  pdf.add_page()
  pdf.set_auto_page_break(auto=True, margin=15)

  # Titel des Dokuments
  pdf.set_font("Helvetica", "B", 16)
  pdf.set_text_color(20, 40, 80)
  pdf.cell(0, 10, f"Wohnungs-{proto_type.lower()}sprotokoll", 0, 1, "C")
  pdf.ln(5)

  # Objektdaten-Box
  pdf.set_font("Helvetica", "B", 10)
  pdf.set_fill_color(240, 244, 248)
  pdf.cell(0, 7, " Objektdaten & Beteiligte", 0, 1, "L", fill=True)

  pdf.set_font("Helvetica", "", 10)
  pdf.set_text_color(50, 50, 50)

  col_w1, col_w2 = 95, 95
  pdf.cell(
      col_w1,
      6,
      f" Objektadresse: {street}, {zip_city} ({floor})",
      0,
      0,
      "L",
  )
  pdf.cell(col_w2, 6, f" Datum: {date.strftime('%d.%m.%Y')}", 0, 1, "L")
  pdf.cell(col_w1, 6, f" Vermieter: {landlord}", 0, 0, "L")
  pdf.cell(col_w2, 6, f" Mieter: {tenant}", 0, 1, "L")
  pdf.cell(0, 6, f" Übergebene Schlüssel: {keys_handed}", 0, 1, "L")
  pdf.ln(5)

  # Zählerstände
  pdf.set_font("Helvetica", "B", 10)
  pdf.set_fill_color(240, 244, 248)
  pdf.cell(0, 7, " Zählerstände", 0, 1, "L", fill=True)

  pdf.set_font("Helvetica", "", 9)
  pdf.cell(
      95,
      6,
      f" Kaltwasser-Zähler (Nr.: {kw_num}): {kw_val} m³",
      0,
      0,
      "L",
  )
  pdf.cell(
      95,
      6,
      f" Warmwasser-Zähler (Nr.: {ww_num}): {ww_val} m³",
      0,
      1,
      "L",
  )

  pdf.cell(
      190,
      6,
      f" Heizkostenverteiler — Wohnzimmer: {h_wz} | Kinderzimmer: {h_kz} |"
      f" Flur: {h_fl}",
      0,
      1,
      "L",
  )
  pdf.cell(
      190,
      6,
      f" Heizkostenverteiler — Bad: {h_ba} | Küche: {h_ku}",
      0,
      1,
      "L",
  )
  pdf.ln(5)

  # Raumzustand & Mängel
  pdf.set_font("Helvetica", "B", 10)
  pdf.set_fill_color(240, 244, 248)
  pdf.cell(0, 7, " Zustand der Räume & Mängel", 0, 1, "L", fill=True)

  # Tabellenkopf
  pdf.set_font("Helvetica", "B", 9)
  pdf.set_fill_color(230, 235, 240)
  pdf.cell(40, 6, "Raum", 1, 0, "C", fill=True)
  pdf.cell(40, 6, "Zustand", 1, 0, "C", fill=True)
  pdf.cell(110, 6, "Mängel / Bemerkungen", 1, 1, "C", fill=True)

  pdf.set_font("Helvetica", "", 9)
  for room, data in room_data.items():
    pdf.cell(40, 6, room, 1, 0, "L")
    pdf.cell(40, 6, data["zustand"], 1, 0, "C")
    m_text = data["maengel"] if data["maengel"].strip() else "Keine Mängel"
    pdf.cell(110, 6, m_text, 1, 1, "L")

  pdf.ln(5)

  # Vereinbarungen
  pdf.set_font("Helvetica", "B", 10)
  pdf.set_fill_color(240, 244, 248)
  pdf.cell(0, 7, " Vereinbarungen & Fristen", 0, 1, "L", fill=True)
  pdf.set_font("Helvetica", "", 9)
  pdf.multi_cell(
      0,
      6,
      agreements if agreements.strip() else "Keine gesonderten Vereinbarungen.",
  )
  pdf.ln(10)

  # Unterschriften
  pdf.set_font("Helvetica", "B", 10)
  pdf.set_fill_color(240, 244, 248)
  pdf.cell(0, 7, " Unterschriften", 0, 1, "L", fill=True)
  pdf.ln(5)

  # Unterschriften-Canvas in PDF einbetten (falls vorhanden)
  sig_y = pdf.get_y()
  pdf.cell(95, 6, " Unterschrift Vermieter", 0, 0, "L")
  pdf.cell(95, 6, " Unterschrift Mieter", 0, 1, "L")
  pdf.ln(20)  Platzhalter für Unterschriftenlinien

  pdf.set_font("Helvetica", "I", 8)
  pdf.set_text_color(100, 100, 100)
  pdf.cell(
      0,
      6,
      "Ort, Datum, Unterschriften bestätigen die Richtigkeit der obigen"
      " Angaben.",
      0,
      1,
      "L",
  )

  # PDF Bytes generieren
  pdf_bytes = pdf.output()

  st.success("Protokoll wurde erfolgreich erstellt!")
  st.download_button(
      label="📥 PDF-Protokoll herunterladen",
      data=pdf_bytes,
      file_name=(
          f"Wohnungsabnahme_{tenant.replace(' ', '_')}_{date.strftime('%Y%m%d')}.pdf"
      ),
      mime="application/pdf",
  )
