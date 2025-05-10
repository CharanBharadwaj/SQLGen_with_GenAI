from flask import Flask, render_template, request, session
from model import LLMModel
import markdown
import re

app = Flask(__name__)

# def generate_sql(natural_query):
#     # Simulated SQL query generation logic
#     # This would be replaced by the actual LLM integration
#     sql_query = f"SELECT * FROM table WHERE column LIKE '%{natural_query}%'"
#     return sql_query

llm_model = LLMModel()

def process_result(generated_text):
    sql_part = None
    input_query = None
    additional_info = None
    split_parts_dummy = None
    if generated_text:
        generated_text = generated_text.strip().replace('<s>','').replace('</s>','')
        if '```' in generated_text:
            split_parts_dummy = generated_text.split('```')
            sql_part = split_parts_dummy[1]
            input_query = split_parts_dummy[0]
            additional_info = '\n'.join(split_parts_dummy[2:])
        elif 'response' in generated_text.lower():
            split_parts_dummy = generated_text.split('Response')
            sql_part = split_parts_dummy[1]
            
            regex = regex = r"(SELECT\s+.*?\s+FROM\s+.*?;)(.*)"
            match = re.search(regex, sql_part, re.IGNORECASE | re.DOTALL)
            sql_part = match.group(1)
            input_query = split_parts_dummy[0]
            additional_info = match.group(2) if match.group(2) else '' 
        else:
            sql_part = "No Result"
        #sql_part = '```' + sql_part + '```'
        #sql_part = markdown.markdown(sql_part).replace('<code>','<code class="sql">')
        sql_part = sql_part.strip()
        input_query = markdown.markdown(input_query).replace('\n','<br/>') if input_query else ''
        additional_info = markdown.markdown(additional_info).replace('\n','<br/>') if additional_info else ''

    return [sql_part,input_query,additional_info]

@app.route('/', methods=['GET', 'POST'])
def index():
    input_query = None
    sql_part = None
    additional_info = None
    if request.method == 'POST':
        natural_query = request.form['query']
        table_schema = request.form['schema']
        natural_query = natural_query.strip()
        table_schema = table_schema.strip()

        if natural_query and table_schema:
            generated_result = llm_model.generate_sql_query(natural_query,table_schema)

        print(generated_result)
        result = process_result(generated_result)
        input_query = result[1]
        additional_info = result[2]
        sql_part = result[0]
        
    return render_template('index.html', input_query=input_query, sql_output=sql_part,additional_info=additional_info)

if __name__ == '__main__':
    app.run(debug=True)