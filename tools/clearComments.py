# -*- coding:utf-8 -*-
import re,os

def pro(targetfn):

    def func(line):
        if line.count('#')==0:
            return line
        if re.match(r'(\t| )*#',line):
            return ''
        line=line[:-1]
        cnt=0
        sline=''
        sli=line.split('#')
        last=len(sli)-1
        for i,x in enumerate(sli):
            cnt+=len(re.findall('"''|'"'",x))
            sline+=x
            if cnt%2==0:
                break
            elif i!=last:
                sline+='#'
        return sline+'\n'
    lis=open(targetfn,encoding='u8').readlines()
    s=''.join([lis[0]]+[func(line) for line in lis[1:]])
    while re.search(r'\n\s*\n',s):
        s=re.sub(r'\n\s*\n','\n',s)
    s=re.sub(r'(\s*\n\s*def)',r'\n\1',s)
    s=re.sub(r'(\s*\n\s*class)',r'\n\1',s)
    s=re.sub(r'(\s*@\w+\n)\n',r'\1',s) 
    open(targetfn,'w',encoding='u8').write(s)
cd=os.path.dirname(os.getcwd())
for root,dirs,files in os.walk(cd):
    for f in files:
        if f[-3:]=='.py' and f[0]!='_':
            p=os.path.join(root,f)
            print(p)
            pro(p)
