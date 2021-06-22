import sys
import os


def print_usage_and_exit():
    print(f'usage: python3 {sys.argv[0]} --web')
    print(f'usage: python3 {sys.argv[0]} --pdf')
    print(f'usage: python3 {sys.argv[0]} --ppt')
    exit(-1)

if len(sys.argv) == 2 and sys.argv[1] == '--web':
    os.system('python3 component/web.py')
elif len(sys.argv) == 2 and sys.argv[1] == '--pdf':
    print(f'yes')
elif len(sys.argv) == 2 and sys.argv[1] == '--ppt':
    print(f'yes')
else:
    print_usage_and_exit()

