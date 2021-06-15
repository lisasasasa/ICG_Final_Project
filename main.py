#import imgkit
from PIL import Image

#imgkit.from_file('index.html', 'out2.jpg')
need_color = []
with open("index.html", "r") as f:
    for line in f.readlines():
        if 'color' in line:
            need_color.append((int(line.split('#')[1][:2], 16), int(line.split('#')[1][2:4], 16), int(line.split('#')[1][4:6], 16)))

for i in need_color:
    print(i)

reply = input("Are you ready?\n")

#Goal: make change list
#https://stackoverflow.com/questions/138250/how-to-read-the-rgb-value-of-a-given-pixel-in-python
pa2pb = {}
im1 = Image.open('pdf_img/12.jpg')
im2 = Image.open('pdf_img_convert/green_and_blue0.jpg')
pix1 = im1.load()
pix2 = im2.load()

def blurry(find):
    if find in need_color:
        return find
    for color in need_color:
        ans = abs(find[0] - color[0]) + abs(find[1] - color[1]) + abs(find[2] - color[2])
        if ans < 4:
            return color
    return None


f2 = open("add.js", "w")
f2.write(
"""
window.addEventListener('DOMContentLoaded', function() {
    x = document.body.querySelectorAll("*");
    for (i = 0; i < x.length; i++) {
""")
w, h = im2.size[0], im2.size[1]
print(type(pix1[10, 20]))
print(pix1[10, 20])
for x in range(w):
    for y in range(h):
        check = blurry(pix1[2 * x, 2 * y])
        if(check != None and pa2pb.get(check) == None):
            pa2pb[check] = pix2[x, y]
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

f2.write(
"""
        }
    }
)
"""
)
#print(pa2pb)

