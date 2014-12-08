def heapifyUp(heap, i, value):
    item = heap[i]
    parentIndex = (i-1)/2
    parent = heap[parentIndex]
    if (parentIndex > -1 and value[parent] > value[item]):
        heap[parentIndex] = item
        heap[i] = parent
        heapifyUp(heap, parentIndex, value)

def heapifyDown(heap, i, value):
    item = heap[i]

    # If item does not have any children
    if not (2*i + 1 < len(heap)):
        return

    # If item does not have a second child or if the first child is lesser than the second child
    if not (2*i + 2 < len(heap)) or (value[heap[2*i + 1]] < value[heap[2*i + 2]]):
        smallerChildIndex = 2*i + 1

    # Otherwise the second child is lesser
    else:
        smallerChildIndex = 2*i + 2

    smallerChild = heap[smallerChildIndex]

    # If necessary, swap the item and the smaller child
    if value[item] > value[smallerChild]:
        heap[i] = smallerChild
        heap[smallerChildIndex] = item
        heapifyDown(heap, smallerChildIndex, value)

def insert(heap, item, value):
    heap.append(item)
    heapifyUp(heap, len(heap)-1, value)

def extractMin(heap, value):
    smallestItem = heap[0]
    heap[0] = heap[len(heap)-1]
    heap.pop()
    if (len(heap) > 0):
        heapifyDown(heap, 0, value)
    return smallestItem

def changeValue(heap, item, newValue, value):
    value[item] = newValue 
    i = heap.index(item)
    parentIndex = (i-1)/2
    parent = heap[parentIndex]

    # If it is not the root (so that it has a parent) and its parent has greater value
    if (parentIndex > -1 and value[parent] > value[item]):
        heapifyUp(heap, i, value)
    else:
        heapifyDown(heap, i, value)
