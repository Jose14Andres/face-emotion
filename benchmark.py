import timeit

setup = """
import random
import string
def generate_filename():
    exts = ['.jpg', '.jpeg', '.png', '.bmp', '.webp', '.txt', '.csv', '.py', '.md', '.json']
    return ''.join(random.choices(string.ascii_lowercase, k=10)) + random.choice(exts)

filenames = [generate_filename() for _ in range(100000)]
extensiones_tuple = ('.jpg', '.jpeg', '.png', '.bmp', '.webp')
extensiones_set = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}
"""

code_tuple = """
count = 0
for f in filenames:
    if f[f.rindex('.'):].lower() in extensiones_tuple:
        count += 1
"""

code_set = """
count = 0
for f in filenames:
    if f[f.rindex('.'):].lower() in extensiones_set:
        count += 1
"""

print("Benchmarking Tuple vs Set for Membership Checking (100,000 files)")
tuple_time = timeit.timeit(code_tuple, setup=setup, number=100)
print(f"Tuple Time: {tuple_time:.4f} seconds")

set_time = timeit.timeit(code_set, setup=setup, number=100)
print(f"Set Time:   {set_time:.4f} seconds")

improvement = ((tuple_time - set_time) / tuple_time) * 100
print(f"Improvement: {improvement:.2f}%")
