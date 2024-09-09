from fastapi import HTTPException
import re


def load_validate(files: list):
    if len(files) != 2:
        raise HTTPException(
            status_code=403,
            detail="File upload failed: needed 2 files!"
        ) 
    for file in files:
        if file.content_type != "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            raise HTTPException(
            status_code=403,
            detail="File upload failed: file not choised or does not fit .xlsx format!"   
        )
        if file.size > 3000000:    
            raise HTTPException(
            status_code=403,
            detail="File upload failed: file size is very big!"
        )


# def filename_validate(file):
#     pattern = re.compile(r'\w+[\-|\.]?\w+')