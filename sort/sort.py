def insert_sort(lists):
    length = len(lists)
    for i in range(1,length):
        key = lists[i]
        j = i - 1
        while j >= 0:
            if lists[j] > key:
                lists[j+1] = lists[j]
                lists[j] = key;
            j -= 1
    return lists
def select_sort(lists):
    length = len(lists)
    for i in range(0,length):
        flag = i
        for j in range(i+1,length):
            if lists[flag] > lists[j]:
                flag = j
        lists[i],lists[flag] = lists[flag],lists[i]
    return lists
def bubble_sort(lists):
    length = len(lists)
    for i in range(0,length):
        for j in range(0,length-i):
            if lists[j+1] > lists[j]:
                lists[j],lists[j+1] = lists[j+1],lists[j] 
    return lists
def quick_sort(lists,begin,end):
    l = begin
    r = end
    flag = lists[l]
    while l<r:
        while l<r and flag >= lists[r]:
            r -= 1
        lists[l] = lists[r]
        while l<r and flag <= lists[l]:
            l += 1
        lists[r] = lists[l]
    lists[r] = flag
    