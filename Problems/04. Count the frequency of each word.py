str = "hello world hello"


def countWords(txt):
    dic = {}
    words = txt.split(" ")
    for w in words:
        dic[w] = dic.get(w, 0) + 1
        
    count = []    
    for k,v in dic.items():
        if v > 1:
            count.append(k)
            
    return count
    
print(countWords(str))
        
