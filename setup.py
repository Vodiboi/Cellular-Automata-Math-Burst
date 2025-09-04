from params import n, SZ
off = (SZ-n)//2
l = ["S", "W"]
with open("initial.txt", "w") as f:
    print(1, SZ, n*n, file=f, sep="\n")
    for i in range(n):
        for j in range(n):
            print(i+off, j+off, l[(i+j)&1], file=f)
