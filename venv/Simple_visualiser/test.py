import numpy as np
array = np.arange(9).reshape(3,3)

print(array)


[_,b] = np.sort(array)

print(b)

for j in range(0,3):
    for i in range(0,np.ma.size(array, 1)):
        array[j][i] = 0

print(array)