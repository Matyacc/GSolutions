#Introduzca el paquete básico requerido
from reportlab.pdfgen import canvas
from reportlab.graphics.barcode import code39, code128, code93
from reportlab.graphics.barcode import eanbc, qr, usps
from reportlab.graphics.shapes import Drawing 
from reportlab.lib.units import mm
from reportlab.graphics import renderPDF


def createBarCodes(c):
    # draw a QR code
    qr_code = qr.QrCodeWidget('Josue Aprende a usar pythonn!!!!')
    bounds = qr_code.getBounds()
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]
    d = Drawing(45, 45, transform=[45./width,0,0,45./height,0,0])
    d.add(qr_code)
    renderPDF.draw(d, c, 15, 700)


c=canvas.Canvas("QR2.pdf")
createBarCodes(c)
c.showPage()
c.save()