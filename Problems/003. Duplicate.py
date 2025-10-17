## duplicate

num = [1, 2, 3, 2, 4, 3, 5]

def dup(no):
    dic = {}
    for i in no:
        dic[i] = dic.get(i, 0) + 1
     
    dup = [] 
    for k, v in dic.items():
        if v > 1:
            dup.append(k)
            
    return dup
    
print(dup(num))


        
