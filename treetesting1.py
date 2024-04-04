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

    current = root
    while current:
        # If id1 matches and id2 is different, go left
        if data['id1'] == current.data['id1'] and data['id2'] != current.data['id2']:
            if current.left is None:
                current.left = Node(data)
                return root
            else:
                current = current.left
        # If id2 matches and id1 is different, go right
        elif data['id2'] == current.data['id2'] and data['id1'] != current.data['id1']:
            if current.right is None:
                current.right = Node(data)
                return root
            else:
                current = current.right
        # Otherwise, move to the next level
        else:
            if data['id1'] < current.data['id1']:
                current = current.left
            else:
                current = current.right
    
    return root

def create_binary_tree(data):
    root_data = data[0]
    root = Node(root_data)
    for d in data[1:]:
        root = insert(root, d)
    return root

def print_pre_order(node):
    if node is None:
        return
    print(node.data, end=" ")
    print_pre_order(node.left)
    print_pre_order(node.right)

# Create the binary tree
root = create_binary_tree(data)

# Print Preorder Traversal
print("Preorder Traversal: ", end="")
print_pre_order(root)
