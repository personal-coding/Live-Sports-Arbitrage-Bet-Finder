import nashpy as nash
import numpy as np


A = np.array([[165 / 100, -1],
              [-1, 160 / 100]])

'''A = np.array([[185/100,-1, -1],
              [-1,  125/100, -1],
              [-1,-1, 280/100]])'''

'''A = np.array([[100/110,-1,-1,-1,-1],
              [-1,300/100,-1,-1,-1],
              [-1,-1,1300/100,-1,-1],
              [-1,-1,-1,200/100,-1],
              [-1,-1,-1,-1,1300/100]])'''

rps = nash.Game(A)

eqs = rps.support_enumeration()
result = list(eqs)[0][0]
print(result)

bet_amount = 100

result = bet_amount * result
result = [round(x) for x in result]

bet_amount = sum(result)

print(result)

sum_val = 0

for m in range(len(result)):
    print((result[m] * A[m][m] / 100 + result[m]) <= bet_amount)
    sum_val += sum(result[m] * A[m])

return_val = sum_val/len(result)
print(return_val, return_val/bet_amount)