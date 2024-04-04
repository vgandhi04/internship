class Node:
    def __init__(self, data):
        self.data = data
        self.left = None
        self.right = None

data = [
        {'id1': "a1", 'id2': "e12"},
        {'id1': "a1", 'id2': "g13"},
        {'id1': "b2", 'id2': "e12"},
        {'id1': "a1", 'id2': "f11"},
        {'id1': "c3", 'id2': "g13"},
        {'id1': "b2", 'id2': "h14"},
        {'id1': "d4", 'id2': "e12"},
        {'id1': "a1", 'id2': "i15"},
        {'id1': "j16", 'id2': "f11"},
        {'id1': "c3", 'id2': "k17"},
        {'id1': "l18", 'id2': "g13"},
        {'id1': "b2", 'id2': "l19"},
        {'id1': "m20", 'id2': "h14"},
        {'id1': "d4", 'id2': "n21"},
        {'id1': "o22", 'id2': "e12"},
    ]

def insert(root, data):
    if root is None:
        root = Node(data)
        return root
    print(f"qqq - {root.data} - {root.left} - {root.right}")
    print(f"data - {data}")
    if data['id1'] == root.data['id1'] and data['id2'] != root.data['id2']:
        # print(f"root - left - {root.left}")
        root.left = insert(root.left, data)
        # print(f"after insert root - left - {root.left.data}")
        structured_arr.append(data)
    elif data['id2'] == root.data['id2'] and data['id1'] != root.data['id1']:
        # print(f"root - right - {root.right}")
        root.right = insert(root.right, data)
        # print(f"after insert root - right - {root.right.data}")
        structured_arr.append(data)
    elif data['id1'] != root.data['id1'] and data['id2'] != root.data['id2']:
        # match with the children of the root node
        print(f"root - left - {root.left} - {root.right}")
        if root.left and (data['id2'] == root.left.data['id2']):
            root.left = insert(root.left, data)
            print(f"data left is {root.left}")
        elif root.right and data['id1'] == root.right.data['id1']:
            root.right = insert(root.right, data)
            print(f"data right is {data}")
    
    return root

def create_binary_tree(data):
    root_data = data[0]
    root = Node(root_data)
    structured_arr.append(root_data)
    for d in data[1:]:
        root = insert(root, d)
    return root

def print_pre_order(node):
    if node is None:
        return
    print(node.data, end=" ")
    print_pre_order(node.left)
    print_pre_order(node.right)

# Defining varilable for tree structure of uservote
total_levels = 3
total_nodes = (2 ** total_levels) - 1
structured_arr = []
root = create_binary_tree(data)

# print(f"{root.data} - {root.left} - {root.right}")
# print(structured_arr)
# Print Preorder Traversal
print("Preorder Traversal: ", end="")
print_pre_order(root)