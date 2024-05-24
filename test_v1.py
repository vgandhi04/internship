numRows = 5
s = "PAYPALISHIRING"

if len(s) == 1 or numRows == 1:
    output = s
else:
    l = [[] for _ in range(numRows)]
    index = (numRows - 1) * 2
    start = 0
    output = ""
    end = start + index
    while len(s) > start:
        if end > len(s):
            end = len(s)
        c = s[start:end]
        start = end
        end = start + index
        ind = 0
        for cha in c:
            print(ind)
            if ind > numRows - 1:
                ind = ind - 1 if ind != numRows else ind -2
                l[ind].append(cha)
                ind -= 1
            else:
                l[ind].append(cha)
                ind += 1
            
            
            
        # for ind, cha in enumerate(c):
        #     if ind > numRows - 1:
        #         l[len(c) - ind].append(cha)
        #     else:
        #         l[ind].append(cha)
        print(l)

    for subset in l:
        output += "".join(subset)

print(output)