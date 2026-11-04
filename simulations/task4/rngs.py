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
random_numbers = []


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
        return exponential(rate, numbers, modulus)




def LCG(multiplier, increment, modulus, seed, count):
    current_value = seed
    random_numbers = []
    for _ in range(count):
        current_value = (multiplier * current_value + increment) % modulus
        random_numbers.append(current_value)
    return random_numbers


def cycle_count(multiplier, increment, modulus, seed):
    current_value = (multiplier * seed + increment) % modulus
    random_numbers = [current_value]
    first_number = current_value

    generated_count = 0
    while True:
        current_value = (multiplier * current_value + increment) % modulus
        random_numbers.append(current_value)
        generated_count += 1
        if current_value == first_number:
            return generated_count


def exponential(rate, numbers, modulus):
    random_numbers = []
    for n in numbers:
        if n == 1:
            random_numbers.append(0) # kan bytla3 -0 somehow????
        else:
            n = 1 - (n / modulus)  # 3ashan tb2a value from from 0 to 1 (never 0 tho)
            random_numbers.append(-math.log(n) / rate)
            
    return random_numbers






def generate_shared_values():
    numbers = LCG(
        multiplier,
        increment,
        modulus,
        seed,
        1000,
    )
    if generator == Generator.EXPONENTIAL:
        numbers = exponential(rate, numbers, modulus)

    random_numbers[:] = numbers
    return random_numbers