import os
folder = r'disclaimer & disclosure'
replacements = [('hello@mainentry.net','hello@sportdgx.com'),('mainentry.net/maria-myers','sportdgx.com')]
for fname in os.listdir(folder):
    if fname.endswith('.html'):
        path = os.path.join(folder, fname)
        text = open(path, encoding='utf-8').read()
        for o, n in replacements:
            text = text.replace(o, n)
        open(path, 'w', encoding='utf-8').write(text)
        print('Fixed:', fname)
