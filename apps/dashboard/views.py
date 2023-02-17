from django.shortcuts import render
from django.views.generic.detail import DetailView
import os
import io
from PIL import Image
import torch
from ast import literal_eval
import collections
from django.core.paginator import Paginator
from django.conf import settings




def landing(request):
    return render(request, 'dashboard/landing.html')

class InferencedImageDetectionView():
    
    template_name = "dashboard/result.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        img_qs = self.get_object()
        imgset = img_qs.image_set
        images_qs = imgset.images.all()

        # For pagination GET request
        self.get_pagination(context, images_qs)

        context["img_qs"] = img_qs
        return context
    
    def get_pagination(self, context, images_qs):
        paginator = Paginator(
            images_qs, settings.PAGINATE_DETECTION_IMAGES_NUM)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context["is_paginated"] = (
            images_qs.count() > settings.PAGINATE_DETECTION_IMAGES_NUM
        )
        context["page_obj"] = page_obj

    def post(self, request,*args, **kwargs):
        model = torch.hub.load(
            'ultralytics/yolov5', 'custom', path='C:/Users/admin/school_study/django-object-detection/apps/dashboard/semi_best_0206_0911.pt', autoshape=True
        )  # force_reload = recache latest code
        model.eval()
        img_qs = self.get_object()
        
        context = {}
        for file in img_qs:
            filename = file.name.rsplit("/")[0]
            img_bytes = file.image.read()
            img = Image.open(io.BytesIO(img_bytes))
            img.save(f"media/detectimage/{filename}",format="JPEG")

            results = model(img,size=640)
            results_list = results.pandas().xyxy[0].to_json(orient="records")
            results_list = literal_eval(results_list)
            classes_list = [item["name"] for item in results_list]
            results_counter = collections.Counter(classes_list)
            if results_list == []:
                pass
            else:
                results.render()
                media_folder = 'media/finddetectimage'
                inferenced_img_dir = os.path.join(
                    media_folder)
                

            for img in results.ims:
                img_base64 = Image.fromarray(img)
                img_base64.save(f"{inferenced_img_dir}/{filename}",format="JPEG")
                        
            context["inferenced_img_dir"] = f"{inferenced_img_dir}/{filename}"
            context["results_list"] = results_list
            context["results_counter"] = results_counter
            
        return render(self.request, self.template_name ,context)
    
def delete_files(request):
    
    directory = ['media/detectimage','media/finddetectimage']
    for direc in directory:
        for filename in os.listdir(direc):
            file_path = os.path.join(direc, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
    return render(request, 'dashboard/delete.html')


            
        


    



