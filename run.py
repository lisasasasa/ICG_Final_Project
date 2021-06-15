need_color = []
with open("index.html", "r") as f:
    for line in f.readlines():
        if 'color' in line:
            need_color.append((int(line.split('#')[1][:2], 16), int(line.split('#')[1][2:4], 16), int(line.split('#')[1][4:6], 16)))

for i in need_color:
    print(i)

