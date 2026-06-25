import xml.etree.ElementTree as ET


def parse_metadata(xml_path: str) -> dict:
    """
    Parse a DFSAR XML file into a flat metadata dictionary.
    """

    tree = ET.parse(xml_path)
    root = tree.getroot()

    metadata = {}

    for elem in root.iter():

        tag = elem.tag.split("}")[-1]

        if elem.text:

            value = elem.text.strip()

            metadata[tag] = value

    return metadata