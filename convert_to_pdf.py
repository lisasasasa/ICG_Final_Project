import os
import PIL
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape

def genpdf(filename,pagesizes):
    pdf = canvas.Canvas(filename)
    pdf.setPageSize(pagesizes)
    return pdf

def save_img_to_pdf(pdf,image,x,y,w,h):
    pdf.drawImage(image,x,y,w,h)
    pdf.showPage()

if __name__ == '__main__':    
    #pdf_size = (2480,3508)
    #my_pdf = genpdf('my_pdf.pdf',pdf_size)
    folder = 'pdf_img'
    filelist = os.listdir(folder)
    flag = True
    for filename in filelist:
        img = PIL.Image.open(folder+'/'+filename)
        if flag == True:
            x,y = img.size
            pdf_size = (x,y)
            my_pdf = genpdf('my_pdf.pdf',pdf_size)
            flag = False
        
        img_w,img_h = img.size
        img_x = (landscape(pdf_size)[1]-img_w)/2
        img_y = (landscape(pdf_size)[0]-img_h)/2
        save_img_to_pdf(my_pdf,folder+'/'+filename,x=img_x,y=img_y,w=img_w,h=img_h)
        print('image'+str(filename)+'saved.')
    my_pdf.save()