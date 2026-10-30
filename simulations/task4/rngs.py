import math


def LCG(multiplier, increment, modulus, seed, count):
    current_value = seed
    random_numbers = []
    for _ in range(count):
        current_value = (multiplier * current_value + increment) % modulus
        random_numbers.append(current_value / modulus)
    return random_numbers


def exponential_rng(rate, numbers):
    random_numbers = []
    for n in numbers:
        random_numbers.append(-math.log(n) / rate)
    return random_numbers