num = [2, 7, 11, 15]
target = 9

def target(no, tar):
    lookup = {}
    for i, num in enumerate(no):
        comp = tar - num
        if comp in lookup:
            return(lookup[comp], i)
        lookup[num] = i
        
print(target(num, target))

op
(0, 1)
