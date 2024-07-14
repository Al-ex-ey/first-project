import os
from fastapi import HTTPException
from src.constants import BASE_DIR#, TEXT_REPLACEMENTS
from docxtpl import DocxTemplate
from fastapi.responses import FileResponse


async def send_reminder():
    pass
    
# async def template_processing(lessee, lease_contract_nomber, lease_contract_date):
#     document_templates_dir = BASE_DIR/"document_templates"
#     document_output_dir = BASE_DIR/"send_files"
#     template_filename = "Template_notification of late payments.docx"
#     output_filename = f"{lessee}_уведомление о повышении арендной платы по договору №{lease_contract_nomber} от {lease_contract_date}.docx"
#     doc = DocxTemplate(document_templates_dir/template_filename)
#     doc.render(TEXT_REPLACEMENTS)
#     doc.save(document_output_dir/output_filename)
#     return output_filename

