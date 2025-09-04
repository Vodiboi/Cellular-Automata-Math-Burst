import os
from PIL import Image

FPS = 60
def num_f(x):
    if x < 5:
        return 60
    elif x < 10:
        return 30
    elif x < 30:
        return 5
    else:
        return 1

a = 965//2
def resized(x, img):
    i2 = img.crop((a, a, 3013-a-1, 3013-a-1))
    if (x < 100):
        return i2.crop((960, 960, 2048-960, 2048-960)).resize((2048, 2048))
    elif x < 1000:
        return i2.crop((768, 768, 2048-768, 2048-768)).resize((2048, 2048))
    else:
        return i2


fp1 = "testfolder"
fp2 = "frames2"
cnt = 0
lst = os.listdir(fp1)
lst.sort(key = lambda x: int(x[3:-4]))
for i, fnm in enumerate(lst):
    img = resized(i, Image.open(f"{fp1}/{fnm}"))
    for j in range(num_f(i)):
        cnt += 1
        img.save(f"{fp2}/{cnt}.png")
