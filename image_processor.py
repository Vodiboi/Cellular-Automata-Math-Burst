from PIL import Image
import os

# fp1 = "bridge_iters"
# fp2 = "bridge_iters_small"
# for i in range(13):
#     img = Image.open(f"bridge_iters/{i}.png")
#     w, h = img.size
#     print(w, h, (500, 0, w-600, h//2))
#     img.crop((600, 250, w-730, 650)).save(f"bridge_iters_small/{i}.png")
fp1 = "fordocdurstpro"
fp2 = "fordocdurstpro_small"
for fl in list(os.listdir(fp1)):
    img = Image.open(f"{fp1}/{fl}")
    w, h = img.size
    # print(w, h, (500, 0, w-600, h//2))
    print("A")
    amt = 450
    img.crop((amt, amt, w-amt, h-amt)).save(f"{fp2}/{fl}")

