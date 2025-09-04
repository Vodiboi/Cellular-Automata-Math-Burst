from PIL import Image
import os
import numpy as np
import sys
# fp1 = "fordocdurst"
# fp1 = "fordocdurstpro"
fp1 = sys.argv[1]
fp2 = fp1
GREEN = (25, 128, 31)
for fl in list(os.listdir(fp1)):
    img = Image.open(f"{fp1}/{fl}")
    w, h = img.size
    print(w, h)
    d = np.array(img.convert("RGBA"))
    r, g, b, a = d.T
    non_black = (r>0) | (b>0) | (g>0)
    d[..., :-1][non_black.T] = GREEN
    i2 = Image.fromarray(d)
    i2.save(f"{fp2}/{fl}")