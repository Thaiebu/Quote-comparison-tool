import pandas as pd
from pypdf import PdfReader

def get_index_by_word(word: str, lines: list[str]) -> int:
    """
    Finds the index of a specific word in a list of lines.

    Args:
        word (str): The word to search for.
        lines (list[str]): The list of lines to search in.

    Returns:
        int: The index of the word in the list of lines, or -1 if not found.
    """
    for i, line in enumerate(lines):
        if word in line:
            return i
    return -1

def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)

    lis = []
    for page in reader.pages:
        lines = page.extract_text().split('\n')
        lis.extend(lines)

    full_text = [line.strip('\n') for line in lis if line.strip()]
    return full_text
    # print(full_text)
 
 

def extraction_template_1(lines: list) -> None:
    """
    Extracts specific data from a PDF file using the PyPDF library.
    Searches for keywords in the text of each page and performs actions based on the keyword found.

    Args:
        pdf_path (str): The path to the PDF file.

    Returns:
        Dictionary with keywords
    """

    # print(full_text)
    full_text = lines
 
    keywords = {
        'Class of Insurance ': lambda line: (line.split('Class of Insurance ')[1]),
        'Name of Insured': lambda line: (line.split('Name of Insured')[1] + full_text[line_index + 1]),
        'Period':lambda line: (line),
        'Scope of Cover': lambda line: (" ".join(full_text[start_index:end_index])),
        'Jurisdiction': lambda line: (line.split('Jurisdiction')[1]),
        'Employers Liability': lambda line: (line.split("Employers Liability")[1]),
        'Deductible': lambda line: (line.split('Deductible')[1]),
        'Clauses': lambda line: (full_text[line_index:end_index]),
        'Exclusions': lambda line: (full_text[line_index:][:10]),
        'Quoe Validity ': lambda line: (full_text[line_index:][1]),
        'Premium': lambda line: (line.split('Premium')[1]),
        'Rate':lambda line: (line.split('Rate')[1]),
        'Number of Employees':lambda line: (line.split(':')[1]),
        'Interest insured':lambda line: (full_text[line_index+1])

    }

    extracted_info = {}

    for line_index, line in enumerate(full_text):
        for keyword, action in keywords.items():
            if keyword in line:
                if keyword == 'Clauses':
                    end_index = get_index_by_word('Exclusions', full_text)                    
                    extracted_info[keyword] = action(line)
                elif keywords == 'Exclusions':
                    extracted_info[keyword] = action(line)
                elif keyword == 'Scope of Cover':
                    start_index = get_index_by_word('Scope of Cover', full_text)
                    end_index = get_index_by_word('Interest insured', full_text)
                    extracted_info[keyword] = action(line)
                elif keyword == 'Interest insured':
                    extracted_info['Estimated Annual'] = action(line)
                
                extracted_info[keyword] = action(line)
    print(extracted_info)
   
    return extracted_info
def extraction_template_2(lines:list) -> None:
    """
    Extracts specific data from a PDF file using the PyPDF library.
    Searches for keywords in the text of each page and performs actions based on the keyword found.

    Args:
        pdf_path (str): The path to the PDF file.

    Returns:
        Dictionary with keywords
    """
    full_text = lines

    keywords = {
        'CLASS OF INSURANCE': lambda line: (line.split('CLASS OF INSURANCE')[1]),
        'NAME OF INSURED': lambda line: ( line.split('NAME OF INSURED')[1]+full_text[line_index+1]),
        'ESTIMATED ANNUAL': lambda line: (full_text[line_index+1]),
        'PERIOD':lambda line:(full_text[line_index+1]),
        'SCOPE OF COVER': lambda line: (full_text[start_index].split('SCOPE OF COVER')[1]+' '.join(full_text[start_index +1:end_index])),
        'JURISDICTION': lambda line: (line.split('JURISDICTION')[1]),
        'LIABILITY': lambda line: (line.split('LIABILITY')[1]),
        'DEDUCTIBLE': lambda line: (line.split('DEDUCTIBLE')[1]),
        'CONDITIONS/CLAUSE': lambda line: (full_text[line_index + 1:end_index]),
        'EXCLUSIONS': lambda line: (full_text[line_index+1 :end_index]),
        'PREMIUM': lambda line: (line.split('PREMIUM')[1]),
        'QUOTATION VALIDITY': lambda line: (line.split('QUOTATION VALIDITY')[1]),
        'RATE':lambda line: (line.split('Rate')[1]),
        'NUMBER OF EMPLOYEES':lambda line: (line.split(':')[1]),
       
    }

    extracted_info = {}

    for line_index, line in enumerate(full_text):
        for keyword, action in keywords.items():
            if keyword in line:
                if keyword == 'CLASS OF INSURANCE':
                    extracted_info['Class of Insurance'] = action(line)
                elif keyword == 'NAME OF INSURED':
                    extracted_info['Name of Insured'] = action(line)
                elif keyword == 'ESTIMATED ANNUAL':
                    extracted_info['Estimated Annual'] = action(line)
                elif keyword == 'QUOTATION VALIDITY':
                    extracted_info['Quoe Validity'] = action(line)
                elif keyword == 'SCOPE OF COVER':
                    start_index = get_index_by_word('SCOPE OF COVER', full_text)
                    end_index = get_index_by_word('JURISDICTION', full_text)
                    extracted_info['Scope of Cover'] = action(line)
                elif keyword == 'CONDITIONS/CLAUSE':
                    end_index = get_index_by_word('EXCLUSIONS', full_text)
                    extracted_info['Clauses']  = action(line)
                elif keyword == 'EXCLUSIONS':
                    end_index = get_index_by_word('PREMIUM', full_text)
                    extracted_info['Exclusions'] = action(line)
                elif keyword == 'Liability':
                    extracted_info['Employers Liability'] = action(line)
                else:
                    extracted_info[keyword.capitalize()] = action(line)
    # extracted_info['Rate'] ='default'
    # extracted_info['Number of Employees'] = 'default'
                
    print(extracted_info)
   
    return extracted_info

def selecting_template_to_extract(pdf_path: str) -> dict:
    """
    Selects the appropriate template for extracting information from a PDF file.
    
    Args:
        pdf_path (str): The path to the PDF file from which to extract information.
        
    Returns:
        dict: A dictionary containing the extracted information from the selected template.
    """
    # Extract text from the PDF
    extracted_lines = extract_text_from_pdf(pdf_path)
    lines = [line for line in extracted_lines]

    keywords_template_1 = [
        'Class of Insurance',
        'Name of Insured',
        'Quoe Validity',
        'Clauses',
        'Exclusions',
        'Premium'
    ]

    keywords_template_2 = [
        'CLASS OF INSURANCE',
        'NAME OF INSURED',
        'QUOTATION VALIDITY',
        'CONDITIONS/CLAUSE',
        'EXCLUSIONS',
        'PREMIUM',
        # Add more keywords for template 2
    ]

    # Count the number of keywords found in the PDF text for each template
    count_template_1 = sum(any(keyword in line for keyword in keywords_template_1) for line in lines)
    count_template_2 = sum(any(keyword in line for keyword in keywords_template_2) for line in lines)

    print(count_template_1, count_template_2)

    # Determine which template to use based on the counts
    if count_template_1 > count_template_2:
        selected_template = 'template_1'
        extracted_data = extraction_template_1(lines)
        print(f"Selected template: {selected_template}")
        return extracted_data
    else:
        selected_template = 'template_2'
        extracted_data = extraction_template_2(lines)
        print(f"Selected template: {selected_template}")
        return extracted_data

# def compare_dicts(dict1, dict2):
#     score_dict1 = 0
#     score_dict2 = 0

#     # Check 'premium' key
#     if 'premium' in dict1 and 'premium' in dict2:
#         score_dict1 += dict1['premium']
#         score_dict2 += dict2['premium']

#     # Check 'rate' key
#     if 'rate' in dict1 and 'rate' in dict2:
#         score_dict1 += 1 if dict1['rate'] == 0.10 else 0
#         score_dict2 += 1 if dict2['rate'] == 0.10 else 0

#     # Check 'deductible' key
#     if 'deductible' in dict1 and 'deductible' in dict2:
#         score_dict1 += dict1['deductible']
#         score_dict2 += dict2['deductible']

#     # Check 'coverage' key (based on text length)
#     if 'coverage' in dict1 and 'coverage' in dict2:
#         score_dict1 += len(dict1['coverage'])
#         score_dict2 += len(dict2['coverage'])

#     # Determine the best dictionary
#     if score_dict1 > score_dict2:
#         return dict1
#     elif score_dict1 < score_dict2:
#         return dict2
#     else:
#         return None  # No clear winner

# # Example dictionaries
# dict1 = {'premium': 1000, 'rate': 0.10, 'deductible': 500, 'coverage': 'Comprehensive coverage'}
# dict2 = {'premium': 1200, 'rate': 0.10, 'deductible': 600, 'coverage': 'Basic coverage'}

# best_dict = compare_dicts(dict1, dict2)
# print(best_dict)
