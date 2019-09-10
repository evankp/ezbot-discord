import random


def random_number(max_num: int = 5):
    random_num_string = ''

    for x in range(max_num):
        random_num_string += str(random.randint(0, 9))

    return random_num_string
