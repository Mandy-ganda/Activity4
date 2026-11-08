"""Programming works: a binary search tree (Laboratory: search, post_traversal, delete_node)."""


class Node:
    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None


class BinaryTree:
    """Binary search tree: smaller keys go left, larger keys go right."""

    def __init__(self):
        self.root = None

    # ---------------------------------------------------------------- insert
    def insert(self, key):
        """Add a key. Returns False if it is already in the tree."""
        if self.root is None:
            self.root = Node(key)
            return True
        cur = self.root
        while True:
            if key == cur.key:
                return False
            side = "left" if key < cur.key else "right"
            nxt = getattr(cur, side)
            if nxt is None:
                setattr(cur, side, Node(key))
                return True
            cur = nxt

    # ------------------------------------------------- LAB METHOD 1: search
    def search(self, root, key):
        """Return the node that holds `key`, or None if it is not in the tree."""
        if root is None or root.key == key:
            return root
        if key < root.key:
            return self.search(root.left, key)
        return self.search(root.right, key)

    # --------------------------------------- LAB METHOD 2: post_traversal
    def post_traversal(self, start, traversal):
        """Post-order: left subtree, right subtree, then the node itself.

        `traversal` is a string that collects the keys, so call it with "":
            tree.post_traversal(tree.root, "")   ->   "20 40 30 60 80 70 50 "
        """
        if start:
            traversal = self.post_traversal(start.left, traversal)
            traversal = self.post_traversal(start.right, traversal)
            traversal += str(start.key) + " "
        return traversal

    # ------------------------------------------- LAB METHOD 3: delete_node
    def delete_node(self, root, key):
        """Delete `key` from the subtree at `root` and return the new subtree root."""
        if root is None:
            return root
        if key < root.key:
            root.left = self.delete_node(root.left, key)
        elif key > root.key:
            root.right = self.delete_node(root.right, key)
        else:
            # Case 1 and 2: no child, or only one child
            if root.left is None:
                return root.right
            if root.right is None:
                return root.left
            # Case 3: two children. Copy the in-order successor, then delete it.
            successor = self.min_node(root.right)
            root.key = successor.key
            root.right = self.delete_node(root.right, successor.key)
        return root

    # --------------------------------------------------------- extra helpers
    def min_node(self, node):
        while node.left:
            node = node.left
        return node

    def in_traversal(self, start, traversal):
        if start:
            traversal = self.in_traversal(start.left, traversal)
            traversal += str(start.key) + " "
            traversal = self.in_traversal(start.right, traversal)
        return traversal

    def pre_traversal(self, start, traversal):
        if start:
            traversal += str(start.key) + " "
            traversal = self.pre_traversal(start.left, traversal)
            traversal = self.pre_traversal(start.right, traversal)
        return traversal

    def delete(self, key):
        self.root = self.delete_node(self.root, key)

    def path_to(self, key):
        """Keys visited while searching for `key` (used to animate the search)."""
        path, cur = [], self.root
        while cur:
            path.append(cur.key)
            if key == cur.key:
                break
            cur = cur.left if key < cur.key else cur.right
        return path

    def size(self, node="root"):
        node = self.root if node == "root" else node
        return 0 if node is None else 1 + self.size(node.left) + self.size(node.right)

    def height(self, node="root"):
        node = self.root if node == "root" else node
        return 0 if node is None else 1 + max(self.height(node.left), self.height(node.right))

    def to_dict(self, node="root"):
        node = self.root if node == "root" else node
        if node is None:
            return None
        return {"value": node.key, "left": self.to_dict(node.left), "right": self.to_dict(node.right)}

    def clear(self):
        self.root = None
