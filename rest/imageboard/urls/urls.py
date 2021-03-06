from django.urls import path, include

urlpatterns = [
    path('main_get/', include('imageboard.urls.post.get_urls')),
    path('main_post/', include('imageboard.urls.post.post_urls')),

    path('user_post/', include('imageboard.urls.user.post_urls')),

    path('moder_get/', include('imageboard.urls.moder.get_urls')),
    path('moder_post/', include('imageboard.urls.moder.post_urls')),
    path('moder_put/', include('imageboard.urls.moder.put_urls')),
    path('moder_delete/', include('imageboard.urls.moder.delete_urls')),

    path('admin_get/', include('imageboard.urls.admin.get_urls')),
    path('admin_post/', include('imageboard.urls.admin.post_urls')),
    path('admin_put/', include('imageboard.urls.admin.put_urls')),
    path('admin_delete/', include('imageboard.urls.admin.delete_urls'))
]