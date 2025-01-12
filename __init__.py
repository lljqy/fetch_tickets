from itertools import groupby

if __name__ == '__main__':
    x = "aabbbccccd"
    for ch, letters in groupby(x):
        print(ch, len(list(letters)))
