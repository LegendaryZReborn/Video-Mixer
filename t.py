'''
import threading

A0 = dict(zip(('a', 'b', 'c', 'd', 'e'), (1, 2, 3, 4, 5)))
A1 = range(10)
A2 = sorted([i for i in A1 if i in A1])


print (A0)
print (A1)

print (A2)

ss = """
To shewing another demands to. Marianne property cheerful informed at striking at. Clothes parlors however by cottage on. In views it or meant drift to. Be concern parlors settled or do shyness address. Remainder northward performed out for moonlight. Yet late add name was rent park from rich. He always do do former he highly. 

Meant balls it if up doubt small purse. Required his you put the outlived answered position. An pleasure exertion if believed provided to. All led out world these music while asked. Paid mind even sons does he door no. Attended overcame repeated it is perceive marianne in. In am think on style child of. Servants moreover in sensible he it ye possible. 
"""
words = {}

for word in ss.split():
	if word in words:
		words[word] += 1
	else:
		words[word] = 1
		
print (words)
		

'''

list = [i for i in range(10)]

for i in list:
	print(i)
	i += 2