import io
import base64
from datetime import datetime
from .models import Notes


def current_time() -> str:
    return datetime.now().strftime("%B %d, %Y at %H:%M:%S")

def get_b64_img(notes_id):
    note = Notes.objects(id=notes_id).first()
    bytes_im = io.BytesIO(note.notes_file.read())
    image = base64.b64encode(bytes_im.getvalue()).decode()
    return image