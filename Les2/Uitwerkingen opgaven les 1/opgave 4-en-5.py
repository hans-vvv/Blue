from collections import defaultdict

combined_sets = defaultdict(set)

set1 = {1,2,3,4}
set2 = {3,4,5,6}

#Q4
for element in set1:
    combined_sets['set1'].add(element)
for element in set2:
    combined_sets['set2'].add(element)

# print(combined_sets)


# Q5, option 1
result = set()
for individual_set in combined_sets:
    for element in combined_sets[individual_set]:
        result.add(element)
# print(result)


# Q5, option 2
result = set()
for individual_set in combined_sets:
    result.update(combined_sets[individual_set])
# print(result)
                


    







