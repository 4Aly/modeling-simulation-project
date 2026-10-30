import math
from enum import Enum


class Generator(Enum):
    LCG = "lcg"
    EXPONENTIAL = "exponential"


generator = Generator.LCG
multiplier = 0
increment = 0
modulus = 0
seed = 0
count = 0
rate = 0


def initialize_variables(
    generator_choice,
    multiplier_value,
    increment_value,
    modulus_value,
    seed_value,
    count_value,
    rate_value,
):
    global generator, multiplier, increment, modulus, seed, count, rate
    generator = generator_choice
    multiplier = multiplier_value
    increment = increment_value
    modulus = modulus_value
    seed = seed_value
    count = count_value
    rate = rate_value


def rng():
    numbers = LCG(multiplier, increment, modulus, seed, count)
    if generator == Generator.LCG:
        return numbers
    if generator == Generator.EXPONENTIAL:
        return exponential(rate, numbers)


def LCG(multiplier, increment, modulus, seed, count):
    current_value = seed
    random_numbers = []
    for _ in range(count):
        current_value = (multiplier * current_value + increment) % modulus
        random_numbers.append(current_value / modulus)
    return random_numbers


def exponential(rate, numbers):
    random_numbers = []
    for n in numbers:
        random_numbers.append(-math.log(n) / rate)
    return random_numbers