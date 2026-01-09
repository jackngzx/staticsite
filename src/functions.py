from textnode import TextNode, TextType
import re


def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)

        else:
            # split the text of node with delimiter. result will be a list
            sections = node.text.split(delimiter)
            if len(sections) % 2 == 0:
                raise Exception("Delimiter error, invalid Markdown syntax")
            # assign each of the items in the list into a new node
            for i in range(0, len(sections)):
                if i % 2 == 0:
                    new_node = TextNode(sections[i], TextType.TEXT)
                    new_nodes.append(new_node)
                else:
                    new_node = TextNode(sections[i], text_type)
                    new_nodes.append(new_node)

    return new_nodes


def extract_markdown_images(text):
    matches = re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
    return matches


def extract_markdown_links(text):
    matches = re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
    return matches

def split_nodes_image(old_nodes):
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)

        else:
            image_tuples = extract_markdown_images(node.text)
            if image_tuples == []:
                new_nodes.append(node)
            current_text = node.text
            for image in image_tuples:
                image_alt = image[0]
                image_url = image[1]
                sections = current_text.split(f"![{image_alt}]({image_url})" , 1)
                if sections[0] is not None:
                    new_nodes.append(TextNode(sections[0], TextType.TEXT))
                    new_nodes.append(TextNode(image_alt, TextType.IMAGE, image_url))
                    current_text = sections[1]
                else:
                    new_nodes.append(TextNode(current_text, TextType.TEXT))
    return new_nodes

            
def split_nodes_link(old_nodes):

