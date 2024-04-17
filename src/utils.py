# from spire.doc import *
# from spire.doc.common import *
from src.constants import BASE_DIR, TEXT_REPLACEMENTS
from docxtpl import DocxTemplate


async def template_processing(lessee, lease_contract_nomber, lease_contract_date):
    document_templates_dir = BASE_DIR/"document_templates"
    document_output_dir = BASE_DIR/"send_files"
    template_filename = "Template_notification of late payments.docx"
    output_filename = f"{lessee}_уведомление о повышении арендной платы по договору №{lease_contract_nomber} от {lease_contract_date}.docx"
    doc = DocxTemplate(document_templates_dir/template_filename)
    doc.render(TEXT_REPLACEMENTS)
    doc.save(document_output_dir/output_filename)
    return output_filename


    # document_templates_dir = BASE_DIR/"document_templates"
    # document_output_dir = BASE_DIR/"send_files"
    # template_filename = "Template_notification of late payments.docx"
    # output_filename = f"{lessee}_уведомление о повышении арендной платы по договору №{lease_contract_nomber} от {lease_contract_date}.pdf"
    # # Create a Document object
    # document = Document()
    # # Load a Word template with placeholder text
    # document.LoadFromFile(template_filename)
    # # Create a dictionary to store the placeholder text and its corresponding replacement text
    # # Each key represents a placeholder, while the corresponding value represents the replacement text
    # text_replacements = TEXT_REPLACEMENTS
    # # Loop through the dictionary
    # for placeholder_text, replacement_text in text_replacements.items():
    # # Replace the placeholder text in the document with the replacement text
    #     document.Replace(placeholder_text, replacement_text, False, False)
    # # Save the resulting document
    # document.SaveToFile(document_output_dir/output_filename, FileFormat.PDF)
    # document.Close()
    # return output_filename