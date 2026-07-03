import sys; sys.path.insert(0, '.')
import format_books as fb

lines = ['वषियसूची', '्र पाठ १ ्र समाज र समुदाय ्र २ ्र']
is_nep = True

print(f'parse_corrupted_num tests:')
print(f'  "१": {fb.parse_corrupted_num("१")}')
print(f'  "ज्ञ": {fb.parse_corrupted_num("ज्ञ")}')
print(f'  "द्द": {fb.parse_corrupted_num("द्द")}')
print(f'  "इकाइ": {fb.parse_corrupted_num("इकाइ")}')

print(f'\nis_noise tests:')
for s in ['समाज र समुदाय', 'ज्ञ', '२', 'पाठ १']:
    print(f'  {s!r}: {fb.is_noise(s)}')

print(f'\nCalling extract_toc_titles:')
try:
    result = fb.extract_toc_titles(lines, is_nep)
    print(f'  Result: ({len(result[0])} entries, end_line={result[1]})')
    for num, title in result[0]:
        print(f'    [{num}] {title}')
except Exception as e:
    import traceback
    traceback.print_exc()

print(f'\nDONE')
