from collections import namedtuple

def fibonacci_generator():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b



def deco(func):
    def wrapper(*args, **kwargs):
        print("before")
        result = func(*args, **kwargs)
        print("after")
        return result
    return wrapper

@deco
def sum(a,b):
    return a + b
  
if __name__ == "__main__":
    # Using the generator to get the first 5 Fibonacci numbers
    # gen = fibonacci_generator()
    # for _ in range(10):
    #     print(next(gen))
    # print("s - ", sum(1,3))
    # words = ["appsale", "mango", "grapes", "fruites", "asdadsasdasd", "asaafdf"]
    # # n = [12,14,12,11,15,5,6,3,0,943,2,-1,155, -10, 121]
    # s_l = sorted(words, key=lambda x : len(x))
    # print(s_l)
    # s_l1 = sorted(words, key=len)
    # print(s_l1)
    # Employee = namedtuple('Employee', ['name', 'department'])
    # john = Employee(name="John", department="IT")
    # print(type(john))
    # my_dict = {i:i for i in range(1, 10)}
    # print(my_dict)
    
    my = []
    
    if my:
        print("hi")
    else:
        print("hello")