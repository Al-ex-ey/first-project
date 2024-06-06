import os
from fastapi import HTTPException
from src.constants import BASE_DIR#, TEXT_REPLACEMENTS
from docxtpl import DocxTemplate
from fastapi.responses import FileResponse


async def template_processing(lessee, lease_contract_nomber, lease_contract_date):
    document_templates_dir = BASE_DIR/"document_templates"
    document_output_dir = BASE_DIR/"send_files"
    template_filename = "Template_notification of late payments.docx"
    output_filename = f"{lessee}_уведомление о повышении арендной платы по договору №{lease_contract_nomber} от {lease_contract_date}.docx"
    doc = DocxTemplate(document_templates_dir/template_filename)
    doc.render(TEXT_REPLACEMENTS)
    doc.save(document_output_dir/output_filename)
    return output_filename


async def load_file():
    path = BASE_DIR/"downloads"
    files_dir = os.listdir(path)
    if "Arenda_2024.xlsx" in files_dir:
       return FileResponse(f"{path}/Arenda_2024.xlsx", media_type = "xlsx", filename="Arenda_2024.xlsx")
    else:
        raise HTTPException(status_code=404, detail="File not found")
    

# async def result_excel_parsing():
#     path = BASE_DIR/"downloads"
#     files_dir = os.listdir(path)
#     if "Arenda_2024.xlsx" in files_dir:
        
#     else:
#         raise HTTPException(status_code=404, detail="File not found")
