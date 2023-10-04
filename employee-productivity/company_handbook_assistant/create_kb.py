from superpowered import create_knowledge_base, create_document_via_text
import os

def upload_documents(data_directory, kb_id, max_documents=1000):
    num_documents = 0
    return_flag = False
    for root, dirs, files in os.walk(data_directory):
        if return_flag:
            break
        for file_name in files:
            # just upload markdown files
            if file_name.endswith('.md'):
                try:
                    file_path = os.path.join(root, file_name)
                    clean_file_path = file_path.replace(data_directory, "") # this will be used as the document title
                    
                    with open(file_path, 'r') as f:
                        text = f.read()

                    # upload files to the Superpowered KB - using relative path as the title adds useful context for the LLM
                    create_document_via_text(knowledge_base_id=kb_id, content=text, title=clean_file_path, auto_context=True)
                    print (f"Uploaded {clean_file_path}")
                except:
                    print (f"Error processing {clean_file_path}")
                    continue

                num_documents += 1
                if num_documents >= max_documents:
                    return_flag = True
                    break

data_directory = 'superpowered-examples/company_handbook_assistant/content'
kb = create_knowledge_base(title='Sourcegraph Handbook', description='Sourcegraph company handbook full text')
kb_id = kb['id']

print (f"Created knowledge base with id {kb_id}")

upload_documents(data_directory=data_directory, kb_id=kb_id, max_documents=1000)