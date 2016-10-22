#!/usr/bin/python

def conv(ssym):
    if ssym == "L":
        return "Q"
    if ssym == "D":
        return "d"
    if ssym == "l":
        return "L"
    if ssym == "s":
        return "H"
    if ssym == "c":
        return "#"
    if ssym == "b":
        return "B"

def convstruct(o):
    n = list(o)
    for i in xrange(0,len(o)):
        n[i] = conv(o[i])
    return "".join(n)

def main():
    for l in open("fmt.csv",'r'):
        t = l.strip().split(',')
        binid =  "\\x%02.x"%(int(t[1]))
        print 'b"%s": SymonTypes(%s, "%s", "%s", []),'%(binid,t[1],t[0], convstruct(t[2]))

if __name__ == "__main__":
    main()
