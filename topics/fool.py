import os,re

cp = os.getcwd()

old = 'answer'
new = 'reply'

cdict=[
    (old+'s',new+'s'),
    (old,new),
    (old.capitalize(),new.capitalize()),
    (old.upper(),new.upper()),
    ('qa_home','tr_home')
    ]

old = 'question'
new = 'topic'

cdict+=[
    (old+'s',new+'s'),
    (old,new),
    (old.capitalize(),new.capitalize()),
    (old.upper(),new.upper()),
    ('qa_home','tr_home')
    ]

for root,dirs,files in os.walk(cp):

    for fn in files:
        if 'fool.py' in fn or '.pyc' in fn:
            continue
        fp=os.path.join(root,fn)
        s=open(fp,encoding='u8').read()
        print(fp)
        for old,new in cdict:
            s=s.replace(old,new)
        open(fp,mode='w',encoding='u8').write(s)

    for old,new in cdict:
        for dn in dirs+files:
            print(root,dn)
            if old in dn:
                os.rename(os.path.join(root,dn),os.path.join(root,dn.replace(old,new)),)
