from PIL import Image
import threading
import os
dir_name = 'component'

def run_pdf():
    os.system("python3 component/pdf_convert_to_jpg.py")

#=============== Collect color from website ===============
print(f'=============== Collect color from website ===============')

#Read line by line to get the color
need_color = []
with open(dir_name + "/index.html", "r") as f:
    for line in f.readlines():
        if 'color' in line:
            need_color.append((int(line.split('#')[1][:2], 16), int(line.split('#')[1][2:4], 16), int(line.split('#')[1][4:6], 16)))
f.close()

for _, color in enumerate(need_color):
    print(f'Color {_}: {color}')

#=============== Wait for color harmonization ===============
#reply = input("Are you ready?\n")
print(f'Waiting for color harmonization')
thread = threading.Thread(target=run_pdf)
thread.start()
thread.join()

#=============== Define blurry function to deal RBG color's problem ===============
def blurry(find):
    if find in need_color:
        return find
    for color in need_color:
        ans = abs(find[0] - color[0]) + abs(find[1] - color[1]) + abs(find[2] - color[2])
        if ans < 4:
            return color
    return None

#=============== Open add.js file ===============
#https://stackoverflow.com/questions/51169182/how-to-insert-one-line-code-in-the-middle-of-the-html-file-by-using-python
src = """
<script src="add.js"></script>
"""
with open(dir_name + "/index.html", "r+") as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
        if '<head>' in line:
            lines[i] = lines[i] + src
    f.truncate()
    f.seek(0)                                           # rewrite into the file
    for line in lines:
        f.write(line)
f.close()

#=============== Open add.js file ===============
f2 = open(dir_name + "/add.js", "w")
f2.write(
"""
window.addEventListener('DOMContentLoaded', function() {
    x = document.body.querySelectorAll("*");
    for (i = 0; i < x.length; i++) {
""")

#=============== Find Color Change list ===============
#https://stackoverflow.com/questions/138250/how-to-read-the-rgb-value-of-a-given-pixel-in-python
image1, image2 = dir_name + '/pdf_img/120.jpg', dir_name + '/pdf_img_convert/red0.jpg'
pa2pb = {}
im1 = Image.open(image1)
im2 = Image.open(image2)
pix1 = im1.load()
pix2 = im2.load()
print(f'Open {image1} and {image2} successfully! Start to write the add.js to change the color !')


# Go through pixel to change the color
w, h = im2.size[0], im2.size[1]
take_color = 0
for x in range(w):
    for y in range(h):
        check = blurry(pix1[2 * x, 2 * y])
        if(check != None and pa2pb.get(check) == None):
            pa2pb[check] = pix2[x, y]
            print(f'Change color {check} to color {pix2[x, y]}')
            take_color = take_color + 1
            f2.write(
            """
            if(x[i].style.backgroundColor == "rgb%s"){
                x[i].style.backgroundColor = "rgb%s";
            }
            if(x[i].style.color == "rgb%s"){
                x[i].style.color = "rgb%s";
            }
            """ %(check,  pix2[x, y],  check, pix2[x, y])
            )
        if take_color is len(need_color):
            break
    if take_color is len(need_color):
            print(f'Finish all color binding!')
            break

f2.write(
"""
        }
    }
)
"""
)
