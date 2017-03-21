import time
from functools import reduce

class Fyve(object):
    """A class to overcomplicate 5."""

    def __call__(self, *args):
        """Basic five."""
        return 5

    def law(self):
        return 'The Law of Fives states simply that: All things happen in fives, or are divisible by or are multiples of five, or are somehow directly or indirectly appropriate to 5. The Law of Fives is never wrong.'

    def up_high(self):
        return '⁵'

    def down_low(self):
        return '₅'

    def roman(self):
        return 'V'

    def convert_to(self, another):
        one_fifth_of_five = self() // self()

        while another < one_fifth_of_five:
            another += one_fifth_of_five

        return another

    def arabic(self):
        return 'خمسة'

    def azerbaijani(self):
        return 'beş'

    def basque(self):
        return 'bost'

    def belarusian(self):
        return 'пяць'

    def bosnian(self):
        return 'pet'

    def bulgarian(self):
        return 'пет'

    def catalan(self):
        return 'cinc'

    def chinese(self, type='default'):
        types = { 'pinyin': 'wǔ', 'financial': '伍', 'default': '五' }
        return types[type]

    def choctaw(self):
        return 'tahlapi'

    def croatian(self):
        return 'pet'

    def czech(self):
        return 'pět'

    def dothraki(self):
        return 'mek'

    def dovah(self):
        return 'hen' 

    def dutch(self):
        return 'vijf' 

    def elvish(self):
        return 'lempe' 

    def english(self):
        return 'five' 

    def esperanto(self):
        return 'kvin' 

    def estonian(self):
        return 'viis' 

    def finnish(self):
        return 'viisi' 

    def french(self):
        return 'cinq' 

    def german(self):
        return 'fünf' 

    def greek(self):
        return 'πέντε' 

    def hebrew(self):
        return 'חמש' 

    def hindi(self):
        return 'पाच' 

    def hungarian(self):
        return 'öt' 

    def icelandic(self):
        return 'fimm' 

    def indonesian(self):
        return 'lima' 

    def irish(self):
        return 'cúig' 

    def italian(self):
        return 'cinque' 

    def japanese(self):
        return '五' 

    def kannada(self):
        return 'ಐದು' 

    def klingon(self):
        return 'vagh' 

    def korean(self):
        return '오' 

    def latin(self):
        return 'quinque' 

    def latvian(self):
        return 'pieci' 

    def lithuanian(self):
        return 'penki' 

    def maltese(self):
        return 'ħamsa' 

    def mongolian(self):
        return 'таван' 

    def nepali(self):
        return 'पाच' 

    def norwegian(self):
        return 'fem' 

    def persian(self):
        return 'پنج' 

    def piglatin(self):
        return 'ivefay' 

    def polish(self):
        return 'pięć' 

    def portuguese(self):
        return 'cinco' 

    def punjabi(self):
        return 'ਪਜ' 

    def romanian(self):
        return 'cinci' 

    def russian(self):
        return 'пять' 

    def serbian(self):
        return 'pet' 

    def slovakian(self):
        return 'päť' 

    def slovenian(self):
        return 'pet' 

    def spanish(self):
        return 'cinco' 

    def swedish(self):
        return 'fem' 

    def tamil(self):
        return 'ஐநது' 

    def telugu(self):
        return 'ఐదు' 

    def turkish(self):
        return 'beş' 

    def thai(self):
        return 'หา' 

    def ukrainian(self):
        return 'п’ять' 

    def welsh(self):
        return 'pump' 

    def morseCode(self):
        return '.....'

    def base(self, base):
        def baseN(num,b):
            """Converts a number to a string representation in any base up to 36."""
            return ((num == 0) and  "0" ) or (baseN(num // b, b).lstrip("0") + "0123456789abcdefghijklmnopqrstuvwxyz"[num % b])
        return baseN(5, base)

    def binary(self):
        return self.base(2)

    def octal(self):
        return self.base(8)

    def hex(self):
        return self.base(16)

    def mdFive(self):
        return '30056e1cab7a61d256fc8edd970d14f5'

    def golden(self):
        # Φ or 'Phyve' = 5 ^ .5 * .5 + .5
        point_five = self() / (self() + self())
        return self() ** point_five * point_five + point_five

    def negative(self):
        return -5;

    def loud(self, lang='english'):
        return getattr(Fyve(), lang)().upper()

    def smooth(self):
        return 'S'

    def too_slow(self):
        time.sleep(self())
        return self()

    def high(self):
        return 'o/'

    def is_five(self, num):
        return num is 5

    def map(self, array):
        return list(map(self, array))

    def filter(self, array):
        return list(filter(self.is_five, array))

    def reduce(self, array):
        return reduce(self, array)

    def fab(self):
        return ['Juwan Howard','Ray Jackson','Jimmy King','Jalen Rose','Chris Webber']

    def jackson(self):
        return ['Jackie','Tito','Jermaine','Marlon','Michael']

    def members(self):
        return ['Sean Conlon', 'Ritchie Neville', 'Scott Robinson', 'Jason \'J\' Brown', 'Abz Love']

    def discography(self):
        return ['5ive', 'Invincible', 'Kingsize']

    def singles(self):
        return ['Slam Dunk (Da Funk)', 'When the Lights Go Out', 'Got the Feelin\'', 'Everybody Get Up', 'It\'s the Things You Do', 'Until the Time Is Through', 'If Ya Gettin\' Down', 'Keep On Movin\'', 'Don\'t Wanna Let You Go', 'We Will Rock You', 'Let\'s Dance', 'Closer to Me', 'Rock the Party', 'I Wish It Could Be Christmas Everyday']

    def furious(self):
        return ['Tigress','Viper','Crane','Monkey','Mantis']

    def luniz(self):
        return "I Got {} on It".format(self())

    def funk(self):
        return "{} bad boys with the power to rock you".format(self())

    def r(self):
        return '£5'

    def rot(self, word):
        if not isinstance(word, str):
            return word

        def replace_letter(l):
            if '0' <= l <= '9':
                return str((int(l) + 5) % 10)
            a_letter = ord('A' if l <= 'Z' else 'a')
            x = 5 + ord(l) - a_letter
            x %= 26
            return chr(x + a_letter)
        shifted = ""
        for c in word:
            shifted += replace_letter(c)
        return shifted

    def oclock(self):
        return '🕔'

    def guys(self):
        return '🍔'

    def 