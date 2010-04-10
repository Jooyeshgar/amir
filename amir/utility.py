def showNumber (number):
    s = str(number)
    l = [x for x in s if x in '1234567890']
    for x in reversed(range(len(s))[::3]):
        l.insert(-x, ',')
    l = ''.join(l[1:])
    return l