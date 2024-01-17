from fastapi import HTTPException


def load_validate(files: list):
    if len(files) != 2:
        raise HTTPException(
            status_code=403,
            detail="File upload failed: needed 2 files!"
        ) 
    for file in files:
        if file.size > 2000000:
            raise HTTPException(
            status_code=403,
            detail="File upload failed: file size is very big!"
        )
        if file.content_type != "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            raise HTTPException(
            status_code=403,
            detail="File upload failed: file not choised or does not fit .xlsx format!"
        )