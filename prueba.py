from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A10
c = canvas.Canvas("hola-mundo.pdf", pagesize=A10)
c.drawString(10, 10, "josu, toga!")
c.save()