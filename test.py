import numpy as np;

result = [];

a = np.array([1,2,3]);
b = np.array([4,5,6]);
c = np.array([7,8,9]);

result.append(a);
result.append(b);
result.append(c);

result = np.array(result)
result = result.flatten().T;

print(result);


