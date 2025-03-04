import xml.etree.ElementTree as ET
import pandas as pd

def extract_fields_from_xml(xml_content, config):
    """
    Extracts fields from an XML content string based on the given configuration.

    Parameters:
        xml_content (str): The XML content as a string.
        config (dict): A dictionary where each key is an XPath string to locate elements,
                       and its value is a list of field names (child tags) to extract.

                       Example:
                       {
                           ".//book": ["title", "author", "price"],
                           ".//person": ["name", "email"]
                       }

    Returns:
        pd.DataFrame: A DataFrame with one row per element found. An extra column 'config'
                      is added to indicate which XPath (configuration group) the row came from.
    """
    # Parse the XML content string
    root = ET.fromstring(xml_content)
    rows = []

    # Iterate over each configuration
    for xpath, fields in config.items():
        # Find all elements matching the XPath
        for elem in root.findall(xpath):
            # Start a row dict; add a 'config' column to indicate the source XPath
            row = {"config": xpath}
            # For each field, attempt to find its child element
            for field in fields:
                child = elem.find(field)
                row[field] = child.text if child is not None else None
            rows.append(row)
    
    # Create a DataFrame from the list of rows
    return pd.DataFrame(rows)

# --- Example Usage ---

xml_string = """
<root>
    <book>
        <title>Book Title 1</title>
        <author>Author 1</author>
        <price>10.99</price>
    </book>
    <book>
        <title>Book Title 2</title>
        <author>Author 2</author>
        <price>12.99</price>
    </book>
    <person>
        <name>John Doe</name>
        <email>john@example.com</email>
    </person>
</root>
"""

# Configuration dictionary:
xml_config = {
    ".//book": ["title", "author", "price"],
    ".//person": ["name", "email"]
}

# Extract the data into a DataFrame
df = extract_fields_from_xml(xml_string, xml_config)

# Display the DataFrame
print(df)
