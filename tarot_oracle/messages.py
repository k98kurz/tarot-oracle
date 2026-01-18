from secrets import token_bytes
from sys import argv

"""Messages from the numinous: divergences from randomized models."""

"""Models take the form of lists of tuples of (monogram, frequency, cummulative frequency)."""
models: dict[str, list[tuple[str, int, int],]] = {
    "english": [
        ('a', 855, 0),
        ('b', 160, 855),
        ('c', 316, 1015),
        ('d', 387, 1331),
        ('e', 1210, 1718),
        ('f', 218, 2928),
        ('g', 209, 3146),
        ('h', 496, 3355),
        ('i', 733, 3851),
        ('j', 22, 4584),
        ('k', 81, 4606),
        ('l', 421, 4687),
        ('m', 253, 5108),
        ('n', 717, 5361),
        ('o', 747, 6078),
        ('p', 207, 6825),
        ('q', 10, 7032),
        ('r', 633, 7042),
        ('s', 673, 7675),
        ('t', 894, 8348),
        ('u', 268, 9242),
        ('v', 106, 9510),
        ('w', 183, 9616),
        ('x', 19, 9799),
        ('y', 172, 9818),
        ('z', 11, 9990)
    ]
}


def get_monogram(model: list[tuple[str, int, int]], modulus: int, randint: int) -> tuple[str, int, int]:
    """Get a monogram from the randomness. Take a model, a modulus, and an int;
        return a monogram from the model and the remaining int.
    """
    val, remainder = divmod(randint, modulus)
    #val, remainder = (0, randint % modulus)
    index, monogram = 0, ''
    for i, m in enumerate(model):
        if m[1] + m[2] > remainder >= m[2]:
            monogram = m[0]
            index = i
            break
    return (monogram, index, val)


def get_distribution(model: list[tuple[str, int, int]], length: int = None) -> list[tuple[str, int]]:
    """Get a distribution of monograms from the randomness. Takes a model;
        returns an ordered list of monograms and counts for each.
    """
    modulus = model[-1][1] + model[-1][2]
    length = length or modulus
    monograms = [[m[0], 0] for m in model]
    val = int.from_bytes(token_bytes(32), 'little')
    count = 0
    while count < modulus:
        monogram, index, val = get_monogram(model, modulus, val)
        count += 1
        monograms[index][1] += 1
        val = int.from_bytes(token_bytes(32), 'little') if val == 0 else val
    return monograms


def get_message(model: list[tuple[str, int, int]], length: int = None) -> list[tuple[str, int]]:
    """Get a message from the randomness. Compare a generated distribution to
        the supplied model and output the difference.
    """
    # get a distribution from a model
    distribution = get_distribution(model, length)

    # compare to the model
    monograms = [[m[0], d[1] - m[1]] for m, d in zip(model, distribution)]
    return monograms


def main(args):
    """The command line interface."""
    print(get_message(models['english']))


if __name__ == '__main__':
    main(argv)
