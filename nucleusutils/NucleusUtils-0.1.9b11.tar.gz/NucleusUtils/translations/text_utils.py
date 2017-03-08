def get_num_ending(number: int, endings: tuple or list) -> str:
    """
    Feature returns the ending for plural words based on the number and array of endings

    Source (JS/PHP): https://habrahabr.ru/post/105428/
    :param number: The number by which you want to generate the end
    :param endings: Array (or tuple) of words or endings for numbers (1, 4, 5) e. g. ('яблоко', 'яблока', 'яблок')
    :return:
    """
    # Fix ending variants list if length < 3
    if len(endings) == 1:
        endings = list(endings) + [endings[0], endings[0]]
    elif len(endings) == 2:
        endings = list(endings) + [endings[1]]

    num = number % 100
    if 11 <= num <= 19:
        return endings[2]
    num %= 10
    if num == 1:
        return endings[0]
    elif 2 <= num <= 4:
        return endings[1]
    return endings[2]
