size = 5
for i in range(size-1, -1, -1):
    for j in range(0, i):
        for k in range(size, i-1, -1):
            print(i, j, k)
