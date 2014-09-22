import os

cp = os.getcwd()

for root,dirs,files in os.walk(cp):
    for fn in files:
        if fn[-4:]=='html':
            path=os.path.join(root,fn)
            s=open(path,encoding='u8').read()
            #print(repr(s[0]))
            if '\ufeff' in s:
                print('del bom for %s'%path)
                open(path,encoding='u8',mode='w').write(s.replace('\ufeff',''))
