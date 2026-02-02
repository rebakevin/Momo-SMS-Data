"""
Data Parser Module for SMS Transaction Data
Converts XML data from assets folder to JSON format
"""

import xml.etree.ElementTree as ET
import json
import os
from pathlib import Path

class DataParser:
    def __init__(self):
        self.xml_file_path = Path(__file__).parent.parent / "app" / "assets" / "modified_sms_v2.xml"
        self.json_output_path = Path(__file__).parent.parent / "assets" / "transactions.json"
        self.parsed_data = None
        self.is_parsed = False
        self.parse_flag_file = Path(__file__).parent.parent / ".data_parsed_flag"
    
    def has_been_parsed(self):
        return self.parse_flag_file.exists()
    
    def mark_as_parsed(self):
        with open(self.parse_flag_file, 'w') as f:
            f.write("Data parsed successfully")
        self.is_parsed = True
    
    def parse_xml_to_json(self):
        """
        Parse XML file and convert to JSON format
        Returns: Dictionary containing parsed data
        Raises: FileNotFoundError, ParseError
        """
        if self.has_been_parsed():
            raise Exception("Data has already been parsed. This endpoint can only be called once.")
        
        if not os.path.exists(self.xml_file_path):
            raise FileNotFoundError(f"XML file not found at {self.xml_file_path}")
        
        if os.path.getsize(self.xml_file_path) == 0:
            raise Exception("XML file is empty. Please add data to the file first.")
        
        try:
            tree = ET.parse(self.xml_file_path)
            root = tree.getroot()
            
            root = tree.getroot()
            
            data = self._parse_element(root)
            self.parsed_data = data
            
            with open(self.json_output_path, 'w') as json_file:
                json.dump(data, json_file, indent=2)
            
            self.mark_as_parsed()
            
            return {
                "success": True,
                "message": "XML data successfully parsed to JSON and saved to transactions.json",
                "data": data,
                "record_count": self._count_records(data),
                "output_file": str(self.json_output_path)
            }
        
        except ET.ParseError as e:
            raise Exception(f"Error parsing XML: {str(e)}")
        except Exception as e:
            raise Exception(f"Error during parsing: {str(e)}")
    
    def _parse_element(self, element):
        """
        Recursively parse XML element to dictionary
        """
        result = {}
        
        if element.text and element.text.strip():
            result['text'] = element.text.strip()
        
        children = list(element)
        if children:
            child_dict = {}
            for child in children:
                child_data = self._parse_element(child)
                child_tag = child.tag
                
                child_tag = child.tag
                
                if child_tag in child_dict:
                    if not isinstance(child_dict[child_tag], list):
                        child_dict[child_tag] = [child_dict[child_tag]]
                    child_dict[child_tag].append(child_data)
                else:
                    child_dict[child_tag] = child_data
            
            result.update(child_dict)
        
            result.update(child_dict)
        
        if len(result) == 1 and 'text' in result:
            return result['text']
        
        return result
    
    def _count_records(self, data):
        """Count the number of records in the parsed data"""
        if isinstance(data, list):
            return len(data)
        elif isinstance(data, dict):
            for key in ['transactions', 'messages', 'records', 'sms']:
                if key in data:
                    return self._count_records(data[key])
            return len(data)
        return 1
    
    def get_parsed_data(self):
        """Return the parsed data"""
        return self.parsed_data
    
    def reset_parse_flag(self):
        """Reset the parse flag (for testing purposes only)"""
        if self.parse_flag_file.exists():
            os.remove(self.parse_flag_file)
        self.is_parsed = False
        if self.json_output_path.exists():
            os.remove(self.json_output_path)
