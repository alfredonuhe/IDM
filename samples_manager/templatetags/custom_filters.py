from django import template
  
register = template.Library()
  
@register.filter()
def num_notation(value, arg):
    """Formats numbers to decimal or scientific notation"""
    try:
        value = float(value)
        if 'd' in arg.lower():
            num_decimal_digits = int(arg[:-1])
            result = str(round(value, num_decimal_digits))
        elif 'e' in arg.lower():
            num_decimal_digits = int(arg[:-1])
            result = ('{:.' + str(num_decimal_digits) + 'E}').format(value)
            split_0 = result.split('E')
            split_1 = split_0[0].split('.')
            remove_digits = 0
            # Remove unnecessary zeros
            for i in range(1, len(split_1[1]) + 1):
                check = ( i < len(split_1[1]))
                if check:
                    increment = (split_1[1][-i] == '0')
                    if increment:
                        remove_digits += 1
                    else:
                        break
                else:
                    break
            split_1[1] = split_1[1][:len(split_1[1]) - remove_digits]
            result = split_1[0] + '.' + split_1[1] + 'E' + split_0[1]
    except:
        result = value
    return result