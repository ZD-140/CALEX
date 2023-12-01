import numpy as np
from scipy.optimize import fsolve

def equation(t):
    x = np.sqrt(98) / 5 * t
    y = 0.3 * np.cos(x) + 1 / (2 * np.sqrt(98)) * np.sin(x) - 1.2
    return y

# 作为起始点，我们从t=0开始
t_initial_guess = 0
t_solution = fsolve(equation, t_initial_guess)

print("满足条件的t值：", t_solution)
