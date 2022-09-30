from celery import shared_task
from PIL import Image as img
import io
from django.core.files.uploadedfile import SimpleUploadedFile
from django.apps import apps


@shared_task
def make_thumbnail(record_pk):
    # Get Image table
    Image = apps.get_model(app_label='socialmedia', model_name='Image')

    # Get the image with passed ID
    record = Image.objects.get(pk=record_pk)

    # Create a scaled down copy
    image = img.open('images/'+str(record.image))
    x_scale_factor = image.size[0]/100
    thumbnail = image.resize((100, int(image.size[1]/x_scale_factor)))
    thumbnail.save("images/test.jpg")

    # Save the copy locally
    byteArr = io.BytesIO()
    thumbnail.save(byteArr, format='jpeg')
    file = SimpleUploadedFile("thumb_"+str(record.image), byteArr.getvalue())

    # Add the copy to the image data in the database
    record.thumbnail = file
    record.save(update_fields=['thumbnail'])
