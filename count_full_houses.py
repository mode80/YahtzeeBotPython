from collections import Counter 

sides=[1,2,3,4,5,6]
full_houses=0; iterations=0
for i in sides:
    for ii in sides:
        for iii in sides:
            for iv in sides:
                for v in sides:
                    iterations+=1
                    permutation = [i,ii,iii,iv,v]
                    counts = sorted(list(Counter(permutation).values()))
                    if (counts[0]==2 and counts[1]==3) or counts[0]==5: full_houses +=1
                    print (permutation, " | ", counts)
print(full_houses, iterations)