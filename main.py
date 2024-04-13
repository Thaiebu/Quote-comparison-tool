from text_extractor import extract_text_from_pdf,extraction_template_1,extraction_template_2
import os
import re, uuid
import pandas as pd
from flask import Flask, request, render_template,send_file
from template import PREDEFINED_LIST,BENIFIT_LIST
app = Flask(__name__)

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

# selecting_template_to_extract(pdf_path)

def get_extracted_dicts_data(folder_path):
    # dicts_data = [data for data in ]
    # Get a list of all files in the folder
    files = os.listdir(folder_path)

    # Filter out only the PDF files
    pdf_files = [file for file in files if file.lower().endswith('.pdf')]
    extracted_datas = {}
    # Print the list of PDF files
    print("PDF Files in the Folder:")
    for pdf_file in pdf_files:
        print(pdf_file)
        data = selecting_template_to_extract(folder_path+'/'+pdf_file)
        extracted_datas[pdf_file] = data
    return extracted_datas
    

def clean_and_get_data(data):
    dicts = {}
    prem_pattern = r'\d{1,3}(?:,\d{3})*(?:\.\d+)?'
    pattern = r'\d+\.\d+|\d+'


    for key,val in data.items():
        if val.get('Premium',False):
            premium = "".join(re.findall(prem_pattern, val['Premium'])[0].split(','))
        else:
            premium = None
        Rate = val.get('Rate','NIL')
        print(Rate)
        if Rate!='NIL':
             matches = re.findall(pattern, Rate)
             numbers =([float(match) if '.' in match else int(match) for match in matches])
             numbers = ['.'.join(map(str, numbers))]
        else:
            numbers = [0]
        # if int(premium) > 0:
        dicts[key] = {'Premium':premium,'Rate':numbers[0],'Deductible':val.get('Deductible','NIL'),'Clauses':val.get('Clauses','None')}
    return dicts

def analyse_ext_data(dicts):
    try:
        # Find the item with the minimum premium
        min_premium = min(v['Premium'] for v in dicts.values() if v['Premium'] is not None)

        # Find all items with the minimum premium
        min_premium_items = [(k, v) for k, v in dicts.items() if v['Premium'] == min_premium]

        # If there are multiple items with the same minimum premium, find the one with the highest rate
        if len(min_premium_items) > 1:
            highest_rate_key = max(min_premium_items, key=lambda x: x[1]['Rate'])[0]
            print(f"Highest rate key for minimum premium: {highest_rate_key}")
            return dicts[highest_rate_key]
        else:
            key, _ = min_premium_items[0]
            dicts[key]['company'] = key
            print(f"Key with minimum premium: {key}")
            return dicts[key]
    except:
        dicts["Error"] = {'Premium': None, 'Rate': 0, 'Deductible': 'NIL', 'Clauses': {}}
        return dicts
        

    # Print the keys for the best quote for each key
    # print("Key for the best premium:", best_premium_key)
    # print("Key for the best rate:", best_rate_key)
    # print("Key for the best deductible:", best_deductible_key)
    # print("Key for the best coverage:", best_coverage_key)
# ext_data = get_extracted_dicts_data('Pdf files')
 
def create_columns(ext_data,clauses):
    columns = {}
    for key,dics in ext_data.items():
        columns[key] = [dics.get('Name of Insured',None),dics.get('Scope of Cover',None),dics.get('Number of Employees',None),dics.get('Jurisdiction',None),dics.get('Period',None),
                    dics.get('Deductible',None),dics.get('Premium',None)]+[s for s in compare_points(clauses[key],PREDEFINED_LIST)]+[dics.get('Rate',None),dics.get('Quoe Validity',None),dics.get('Estimated Annual',None)]
    return columns
def get_clause(dicts):
    clauses={}
    for key, dictionary in dicts.items():
        clauses[key]=' '.join(dictionary['Clauses'])
    return clauses
def compare_points(input_list, predefined_list):
    count=0
    comment = []
    for key,line in predefined_list.items():
        key=key.replace('-', '')
        if key.lower() in input_list.replace('-', ''):
            comment.append("yes")
        else:
            comment.append("no")
            count+=1
    return comment     
          


@app.route('/')
def home():
    delete_files_in_folder('Pdf files')
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    
    if request.method == 'POST':
        files = request.files.getlist('file')
        # Generate a random UUID
        random_uuid = str(uuid.uuid4())
        path = []
        combined_data = {}
        if files:
            for file in files:
                file.save('Pdf files/'+file.filename)
                path.append('Pdf files/'+file.filename)
            if len(files) >= 2: 
                ext_data = get_extracted_dicts_data('Pdf files')
                clean_dict = clean_and_get_data(ext_data)
                anal_data = analyse_ext_data(clean_dict)
                comp = anal_data.get('company',None)
                if comp is not None:
                    comp = comp.split('.')[0]
                dicts = {"Premium" :anal_data.get('Premium',None),"Rate":anal_data.get('Rate',None),"Deductible":anal_data.get('Deductible',None),"Minimum deposit premium":"None","Commission":"None"}
                if dicts['Premium'] == None and dicts['Rate']==None:
                    return "Error : Upload Valid PDF "
                else:
                    clauses = get_clause(clean_dict)
                    combined_data['Benifits'] = BENIFIT_LIST
                    combined_data.update(create_columns(ext_data,clauses))
                    # print(len(BENIFIT_LIST),len(combined_data['QIC Quote.pdf']),len(combined_data['Sharq Quote.pdf']))
                    df = pd.DataFrame(combined_data)
                    filename = f'output_{random_uuid[:7]}.xlsx'
                    df.to_excel('Pdf files/'+ filename, index=False)
                    print(df)
                    clauses = [ line for line in anal_data['Clauses'] if len(line.split(' ')) > 4]
                    print(clauses)
                    # html_table = df.to_html()

            return render_template('report.html',comp = comp,dicts=dicts,df = df,filename=filename,clauses=clauses[:9])

@app.route('/download_excel/<filename>')
def download_excel(filename):
    # Assume filename is the parameter passed in the URL
    # Use the filename parameter to construct the file path
    filepath = 'Pdf files/' + filename 
    return send_file(filepath, as_attachment=True)

@app.route('/about')
def about():
    return render_template('UserManual.html')
        
            
def delete_files_in_folder(folder_path):
    try:
        # List all files in the folder
        files = os.listdir(folder_path)
        for file in files:
            # Construct the full path to the file
            file_path = os.path.join(folder_path, file)
            # Check if the file is a regular file (not a directory)
            if os.path.isfile(file_path):
                # Delete the file
                os.remove(file_path)
        return True
    except Exception as e:
        print(f"Error deleting files: {e}")
        return False

if __name__ == '__main__':
    app.run(port = 82)
    
