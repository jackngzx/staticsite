from textnode import TextNode, TextType


class HTMLNode:
    def __init__(self, tag=None, value=None, children=None, props=None):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def to_html(self):
        raise NotImplementedError

    def props_to_html(self):
        final_string = ""
        if self.props is None or self.props == {}:
            return final_string
        for key, value in self.props.items():
            final_string += f' {key}="{value}"'
        return final_string

    def __repr__(self):
        return f"HTMLNode({self.tag}, {self.value}, children: {self.children}, {self.props})"


class LeafNode(HTMLNode):
    def __init__(self, tag, value, props=None):
        super().__init__(tag, value, None, props)

    def to_html(self):
        if self.value is None:
            raise ValueError("Value is missing")
        if self.tag is None:
            return f"{self.value}"
        return f"<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>"

    def __repr__(self):
        return f"LeafNode({self.tag}, {self.value}, {self.props})"


class ParentNode(HTMLNode):
    def __init__(self, tag, children, props=None):
        super().__init__(tag, None, props)
        self.children = children

    def to_html(self):
        if self.tag is None:
            raise ValueError("Tag is missing")
        if self.children is None:
            raise ValueError("No children")

        childrens_html = ""
        for childrens in self.children:
            childrens_html += childrens.to_html()

        open_tag = f"<{self.tag}{self.props_to_html()}>"
        close_tag = f"</{self.tag}>"

        final_string = open_tag + childrens_html + close_tag

        return final_string

    def __repr__(self):
        return f"ParentNode({self.tag}, children: {self.children}, {self.props})"


def text_node_to_html_node(text_node):
    if text_node.text_type.value == TextType.TEXT:
        return LeafNode(None, text_node.text)
    if text_node.text_type.value == TextType.BOLD:
        return LeafNode("b", text_node.text)
    if text_node.text_type.value == TextType.ITALIC:
        return LeafNode("i", text_node.text)
    if text_node.text_type.value == TextType.CODE:
        return LeafNode("code", text_node.text)
    if text_node.text_type.value == TextType.LINK:
        return LeafNode("a", text_node.text, "href")
    if text_node.text_type.value == TextType.IMAGE:
        return LeafNode("img", "", {"src", "alt"})


raise Exception("No TextNode type matched")
