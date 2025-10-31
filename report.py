from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
import os, time, json

def generate_user_report(username, progress_list, out_path):
    c = canvas.Canvas(out_path, pagesize=A4)
    width, height = A4
    c.setFont('Helvetica-Bold', 16)
    c.drawString(30*mm, height - 30*mm, f'ICS Training Report for {username}')
    c.setFont('Helvetica', 10)
    c.drawString(30*mm, height - 36*mm, f'Date: {time.ctime()}')
    y = height - 50*mm
    c.setFont('Helvetica-Bold', 12)
    c.drawString(30*mm, y, 'Module Results:')
    y -= 8*mm
    c.setFont('Helvetica', 10)
    if not progress_list:
        c.drawString(30*mm, y, 'No progress recorded.')
    for p in progress_list:
        line = f"- {p['module']}: {p['score']}% @ {time.ctime(p['timestamp'])}"
        c.drawString(32*mm, y, line)
        y -= 6*mm
        # limit to page
        if y < 30*mm:
            c.showPage()
            y = height - 30*mm
    c.showPage()
    c.save()
    return out_path
