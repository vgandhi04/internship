class Node:
    def __init__(self, data):
        self.data = data
        self.left = None
        self.right = None

def insert(root, data):
    if root is None:
        return Node(data)
    
    if data['id1'] == root.data['id1']:
        if data['objid'] != root.data['objid']:
            if data['id2'] == root.data['id2']:
                if data.get('objid') == root.data.get('objid'):
                    return root
                elif root.data.get('objid') is None:
                    root.data['objid'] = data['objid']
                    return root
            elif data['id2'] < root.data['id2']:
                root.left = insert(root.left, data)
            else:
                root.right = insert(root.right, data)
        return root
    
    if data['id2'] == root.data['id2']:
        if data['objid'] != root.data['objid']:
            if data['id1'] < root.data['id1']:
                root.left = insert(root.left, data)
            else:
                root.right = insert(root.right, data)
        return root
    
    if data['id1'] < root.data['id1']:
        root.left = insert(root.left, data)
    else:
        root.right = insert(root.right, data)
    return root

def generate_data():
    data = [
        {'id1': 1, 'id2': 12, 'objid': 101},
        {'id1': 1, 'id2': 13, 'objid': 102},
        {'id1': 2, 'id2': 12, 'objid': 103},
        {'id1': 1, 'id2': 11, 'objid': 104},
        {'id1': 3, 'id2': 13, 'objid': 105},
        {'id1': 2, 'id2': 14, 'objid': 106},
        {'id1': 4, 'id2': 12, 'objid': 107}
    ]
    return data

def create_binary_tree(data):
    root_data = data[0]
    root = Node(root_data)
    for d in data[1:]:
        insert(root, d)
    return root

def get_left_node(root):
    if root.left:
        return root.left.data
    else:
        return None

def get_right_node(root):
    if root.right:
        return root.right.data
    else:
        return None

def main():
    data = generate_data()
    root = create_binary_tree(data)

    print("Binary Tree has been created.")

    print("\nLevel 0: root node - id1 =", root.data['id1'], ", id2 =", root.data['id2'])
    
    left_node = get_left_node(root)
    right_node = get_right_node(root)
    
    print("Level 1: Left Node - id1 =", left_node['id1'], ", id2 =", left_node['id2'])
    print("Level 1: Right Node - id1 =", right_node['id1'], ", id2 =", right_node['id2'])
    
    if left_node:
        left_left_node = get_left_node(root.left)
        left_right_node = get_right_node(root.left)
        if left_left_node:
            print("Level 2: Left node of level 1's left node - id1 =", left_left_node['id1'], ", id2 =", left_left_node['id2'])
        else:
            print("Level 2: Left node of level 1's left node - None")
        if left_right_node:
            print("Level 2: Right node of level 1's left node - id1 =", left_right_node['id1'], ", id2 =", left_right_node['id2'])
        else:
            print("Level 2: Right node of level 1's left node - None")
    
    if right_node:
        right_left_node = get_left_node(root.right)
        right_right_node = get_right_node(root.right)
        if right_left_node:
            print("Level 2: Left node of level 1's right node - id1 =", right_left_node['id1'], ", id2 =", right_left_node['id2'])
        else:
            print("Level 2: Left node of level 1's right node - None")
        if right_right_node:
            print("Level 2: Right node of level 1's right node - id1 =", right_right_node['id1'], ", id2 =", right_right_node['id2'])
        else:
            print("Level 2: Right node of level 1's right node - None")

if __name__ == "__main__":

    data = generate_data()
    root = create_binary_tree(data)

    print("Binary Tree has been created.")

    print("\nLevel 0: root node - id1 =", root.data['id1'], ", id2 =", root.data['id2'])
    
    left_node = get_left_node(root)
    right_node = get_right_node(root)
    
    print("Level 1: Left Node - id1 =", left_node['id1'], ", id2 =", left_node['id2'])
    print("Level 1: Right Node - id1 =", right_node['id1'], ", id2 =", right_node['id2'])
    
    if left_node:
        left_left_node = get_left_node(root.left)
        left_right_node = get_right_node(root.left)
        print("Level 2: Left node of level 1's left node - id1 =", left_left_node['id1'], ", id2 =", left_left_node['id2'])
        print("Level 2: Right node of level 1's left node - id1 =", left_right_node['id1'], ", id2 =", left_right_node['id2'])
    
    if right_node:
        right_left_node = get_left_node(root.right)
        right_right_node = get_right_node(root.right)
        print("Level 2: Left node of level 1's right node - id1 =", right_left_node['id1'], ", id2 =", right_left_node['id2'])
        print("Level 2: Right node of level 1's right node - id1 =", right_right_node['id1'], ", id2 =", right_right_node['id2'])

if __name__ == "__main__":
    main()
