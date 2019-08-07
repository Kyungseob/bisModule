import os;

abs = os.path.dirname(os.path.abspath(__file__));
test1 = os.path.join('test', 'test2');
test2 = os.path.join('test', 'test1');

result = os.path.join(abs, test1, test2);
print(result);


