import re

# Check what characters match in [०१२३४५६७८९]
chars_to_test = ['१', '२', 'द', '्', 'ध', 'ज', '्ञ']
dev_digits = set('०१२३४५६७८९')

for c in chars_to_test:
    in_digits = c in dev_digits
    print(f'{c!r} (U+{ord(c):04X}): in_dev_digit_class={in_digits}')

# Test regex character class
pat_class = re.compile(r'^[०१२३४५६७८९]+$')
test_strings = ['१', '२', 'द्ध', 'ज्ञ', '१२']
for s in test_strings:
    m = pat_class.match(s)
    print(f'  \"{s}\" matches digit class: {bool(m)}')
