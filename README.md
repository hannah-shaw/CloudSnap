# CloudSnap
CloudSnap: A Serverless Image Storage System with Tagging


This work aims to build a cloud-based online system that allows users to store and retrieve images based on auto-generated tags. The focus of this project is to design a serverless application that enables clients to upload their images to public cloud storage. Upon image upload, the application automatically tags the image with the objects detected in it, such as person, car, etc. Later on, clients can query images based on the objects present in them. To achieve this, the application provides users with a list of image URLs (or tumbnails) that include the specific queried objects.

Testing
## 目前测试阶段点击begin.html进入初始界面，若想跳过登录验证直接点击右上方welcome
## 登陆注册修改，测试callback,注册完直接算登录，和登录完直接跳转到upload 具体url：localhost:8080/upload