import unittest

from htmlnode import HTMLNode, LeafNode, ParentNode, text_node_to_html_node
from textnode import TextNode, TextType


class TestHTMLNode(unittest.TestCase):
    def test_eq(self):
        node = HTMLNode("p", "hello", "a, b, c", {"href": "http://www.google.com"})
        node2 = HTMLNode("p", "hello", "a, b, c", {"href": "http://www.google.com"})
        self.assertEqual(node.tag, node2.tag)
        self.assertEqual(node.value, node2.value)
        self.assertEqual(node.children, node2.children)
        self.assertEqual(node.props, node2.props)

    def test_not_eq(self):
        node = HTMLNode("p", "hello", "a, b, c", {"href": "http://www.google.com"})
        node2 = HTMLNode("a", "hello", "a, b", {"href": "http://www.google.com"})
        self.assertNotEqual(node, node2)

    def test_props_to_html(self):
        node = HTMLNode(
            "p",
            "hello",
            "a, b, c",
            {"href": "https://www.google.com", "target": "_blank"},
        )
        test_string = ' href="https://www.google.com" target="_blank"'
        self.assertEqual(node.props_to_html(), test_string)

    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")

    def test_leaf_to_html_a(self):
        node = LeafNode("a", "Click me!", {"href": "https://www.google.com"})
        self.assertEqual(
            node.to_html(), '<a href="https://www.google.com">Click me!</a>'
        )

    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )

    def test_text(self):
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")


if __name__ == "__main__":
    unittest.main()
