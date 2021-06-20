import win32com.client
import os
print("input ppt filename")
path = input()
def PPT_to_PDF(in_path, out_path):
    powerpoint = win32com.client.Dispatch("Powerpoint.Application")
    pdf = powerpoint.Presentations.Open(in_path, WithWindow=False)
    pdf.SaveAs(out_path, 32)
    pdf.Close()
    powerpoint.Quit()
save_path = 'test.pdf'
infile = os.path.abspath(path)
outfile = os.path.abspath(save_path)
PPT_to_PDF(infile, outfile)