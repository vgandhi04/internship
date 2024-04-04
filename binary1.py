def generate_data():
    data = [
        {'id1': 1, 'id2': 12, 'objid': 101},
        {'id1': 1, 'id2': 13, 'objid': 101},
        {'id1': 2, 'id2': 12, 'objid': 101},
        {'id1': 1, 'id2': 11, 'objid': 101},
        {'id1': 3, 'id2': 13, 'objid': 101},
        {'id1': 2, 'id2': 14, 'objid': 101},
        {'id1': 4, 'id2': 12, 'objid': 101}
    ]
    return data

def insert(root, data):
    if root is None:
        return Node(data)
    if data['id1'] < root.data['id1']:
        root.left = insert(root.left, data)
    elif data['id2'] > root.data['id2']:
        root.right = insert(root.right, data)
    return root

data = generate_data()
root = None
for item in data:
    root = insert(root, item)