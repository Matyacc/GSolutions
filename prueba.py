direccion = "nicaragua 1720"
localidad = "Canning"
telefono = "1527160925"
nombre = "Matias Acciaio"

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import personalizado
import os
archivo = "hola-mundo.pdf"
c = canvas.Canvas(archivo, pagesize=personalizado)
c.setFont("Helvetica", 16)
c.drawString(5, 30,direccion)
c.drawString(5, 50,localidad)
c.drawString(5, 70,telefono)
c.drawString(5, 90,nombre)
c.save()
os.startfile(archivo,"print")
