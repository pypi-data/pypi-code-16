regex_currency = ["(RS|RE|INR|Rupees|\u20B9|Balance:|Bal:|cost:)[\.]?[\s]?(\d+[,]?\d*[,]?\d*[,]?\d*)"]

regex_date = ["([0]?[1-9]|[1|2][0-9]|[3][0|1])[-./]([0]?[1-9]|[1][0-2])[-./]([0-9]{4}|[0-9]{2})","([0]?[1-9]|[1|2][0-9]|[3][0|1])[-./\s]?(January|February|March|April|May|June|July|August|September|October|November|December)[-./\s]?([0-9]{4}|[0-9]{2})?","([0]?[1-9]|[1|2][0-9]|[3][0|1])[-./\s]?(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[-./\s]?([0-9]{4}|[0-9]{2})?","([0-9]{4}|[0-9]{2})[-./]([0]?[1-9]|[1|2][0-9]|[3][0|1])[-./]([0]?[1-9]|[1][0-2])","([0]?[1-9]|[1][0-2])[-./]([0]?[1-9]|[1|2][0-9]|[3][0|1])[-./]([0-9]{4}|[0-9]{2})"]

regex_email = "(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,4}$)"

regex_pan = "(^[A-Z]{3}[A|B|C|F|G|H|L|J|P|T|K][A-Z][0-9]{4}[A-Z]$)"

regex_distance = ["(\d+[.]?\d*?)[\s]*?(kilometer|mile|km|meters|meter)"]

regex_time_duration = ["([0-9]+)[:]([0-9]+)[:]?([0-9]+)?","([0-9]+\s*(hours|hour|hr)\s+)?([0-9]+\s*(minutes|minute|mins|min)\s+)?([0-9]+\s*(seconds|second|secs|sec))"]

regex_internet_data = ["(\d+[.]?\d*?)[\s]*?(mb|kb|byte|gb)"]

regex_time = ["([01]?[0-9]|2[0-3]):([0-5]?[0-9])?:([0-5]?[0-9])?","([01]?[0-9]|2[0-3]):?([0-5]?[0-9])?\s?(AM|PM)[\b\.\s]"]