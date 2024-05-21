from botocore.exceptions import ClientError
from django.shortcuts import render
from django.db import IntegrityError
from django.shortcuts import redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import SubirDumentoImagenForm
from .models import SubirDumentoImagen

from django.http import HttpResponse

import boto3
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv


@login_required
def upload(request):
    form = SubirDumentoImagenForm()
    if request.method == "POST":
        try:
            form = SubirDumentoImagenForm(request.POST, request.FILES)
            if form.is_valid():
                post = form.save(commit=False)
                post.user_contact_id = request.user.id
                post.save()
                return render(request, 'index.html', {'form': form, 'message': 'Archivos se subieron con éxito'})
            else:
                return render(request, 'index.html', {'form': form, 'message': 'Error de formulario'})
        except:
            return render(request, 'index.html', {'form': form, 'message': 'No se pudo subir a la base de datos'})
    else:
        return render(request, 'index.html', {'form': form})


@login_required
def listarData(request):
    data = SubirDumentoImagen.objects.filter(user_contact_id=request.user.id)
    
    
    return render(request=request, template_name="list_img_file.html", context={'data': data})


@login_required
def delete(request, folder, object):
    _path = f"{folder}/{object}"
    data = SubirDumentoImagen.objects.filter(user_contact_id=request.user.id)
    data_documento = data.values().filter(documento=_path)
    data_imagen = data.values().filter(imagen=_path)
    
    print(data_documento, data_imagen)
    if request.method == 'POST':
        print(_path)
    else:
        s3_client = boto3.client(
            's3',
            aws_access_key_id='AKIA2UC3FPP6NNB52ATZ',
            aws_secret_access_key='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'
        )
        bucket_name = 'archivos-bucket'
        object_key = _path

        try:
            s3_client.delete_object(Bucket=bucket_name, Key=object_key)
            print(f'El objeto {object_key} fue eliminado exitosamente de {bucket_name}.')
            if data_documento.count() > 0:
                data_documento.update(documento="")
            if data_imagen.count() > 0:
                data_imagen.update(imagen="")
            return redirect("/lista-de-registros/", {"message":"error"})
        except ClientError as e:
            # Imprime el error si ocurre
            print(f'Error al eliminar el objeto: {e}')
            return redirect("/lista-de-registros/", {"message":"error"})

def user_login(request):
    if request.method == 'GET':
        if request.user.id is not None:
            return redirect('/upload')
        else:
            return render(request, 'login.html')
    else:
        username = request.POST['username']
        password = request.POST['password']

        findUser = authenticate(request, username=username, password=password)
        print(findUser)

        if username != '' and password != '':
            if findUser is not None:
                try:
                    login(request, findUser)
                    return redirect('/upload')
                except IntegrityError:
                    return render(request, 'login.html', {
                        'error': 'No se puede ingresar'
                    })
            else:
                return render(request, 'login.html', {
                    'error': 'Nombre de usuario y contraseña no existe'
                })
        else:
            return render(request, 'login.html', {
                'error': 'Se requieren rellenar los campos'
            })


def user_logout(request):
    logout(request)
    return redirect('/')


def user_register(request):
    if request.method == 'GET':
        if request.user.id is not None:
            return redirect('/upload')
        else:
            return render(request, 'register.html')
    else:
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        findUser = User.objects.filter(username=username).exists()
        print(findUser)

        if findUser != True:
            if username != '' and email != '' and password != '':
                try:
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=password,
                    )
                    user.save()
                    login(request, user)
                    return redirect('/upload')
                except IntegrityError:
                    return render(request, 'register.html', {
                        'error': 'No se puede ingresar'
                    })
            else:
                return render(request, 'register.html', {
                    'error': 'Se requieren rellenar los campos'
                })
        else:
            return render(request, 'register.html', {
                'error': 'Nombre de usuario existente'
            })
