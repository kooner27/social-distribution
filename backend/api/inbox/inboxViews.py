### models and serializers
from ..models import Author, AuthorFollower, Post, Like, Comment, Inbox
from ..authors.serializers import UserSerializer, AuthorSerializer, AuthorDetailSerializer
from ..posts.serializers import PostSerializer
from .serializers import LikeSerializer, InboxSerializer, PostLikeSerializer
from django.contrib.auth.models import User
##### user auth
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
##### views
from rest_framework import generics, views, permissions, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.decorators import api_view
## from django
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseNotFound
from datetime import datetime
from django.utils import timezone
from rest_framework import pagination
import uuid
import base64
from django.urls import resolve



class PostLikesListView(generics.ListAPIView):
    serializer_class = PostLikeSerializer

    def get_queryset(self):
        author_id_hex = self.kwargs['author_id']
        post_id_hex = self.kwargs['post_id']
        try:
            post_id = uuid.UUID(hex=post_id_hex)
        except ValueError:
            # Handle invalid UUIDs here, such as returning an error response
            return []

        return Like.objects.filter(liked_post_id=post_id)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        likes_data = serializer.data
        
        # Create a custom response dictionary with "items" as the key
        response_data = {"type": "likes", "items": likes_data}
        
        return Response(response_data)



class InboxView(generics.RetrieveUpdateAPIView):
    queryset = Inbox.objects.all()
    serializer_class = InboxSerializer
    # lookup_field = 'author__pk'

    def retrieve(self, request, *args, **kwargs):
        # You can override the default behavior if you want, otherwise just let it return the serialized object.
        return super().retrieve(request, *args, **kwargs)

    # handle POST request for post, follow, comment, like
    def update(self, request, *args, **kwargs):
        data = request.data
        object_type = data.get('type')
        if not object_type:
            return Response({"error": "No type provided"}, status=status.HTTP_400_BAD_REQUEST)

        object_type = object_type.lower() 

        if object_type not in ['post', 'comment']:
            return Response({"message": "Type not supported"}, status=status.HTTP_400_BAD_REQUEST)

        # add the post or comment to the inbox
        
        instance = self.get_object()
        instance.add_item(data)
        instance.save()

        return Response({"message": "Item added to inbox successfully"}, status=status.HTTP_201_CREATED)













#TODO: handle all types
@api_view(['POST'])
def inbox_view(request, author_id):
    data = request.data
    object_type = data.get('type')
    object_type = object_type.lower()

    if not object_type:
        return Response({"error": "No type provided"}, status=status.HTTP_400_BAD_REQUEST)

    
    if object_type not in ['post', 'comment']:
        return Response({"message": "Type not supported"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        author = Author.objects.get(author_id)
        # retrieve the author's inbox
        author_inbox = Inbox.objects.get(author=author)

    except Author.DoesNotExist:
        return Response({"error": "Author not found"}, status=status.HTTP_404_NOT_FOUND)
    except Inbox.DoesNotExist:
        return Response({"error": "Inbox not found for the author"}, status=status.HTTP_404_NOT_FOUND)

    # add the post or comment to the inbox
    author_inbox.add_item(data)

    return Response({"message": "Item added to inbox successfully"}, status=status.HTTP_201_CREATED)

class InboxView(generics.CreateAPIView):
    def get_serializer_class(self):
        return LikeSerializer    
    ## get the owner of the inbox
    def get_author(self):
        author_id_hex = self.kwargs['author_id']
        try:
            author_id = uuid.UUID(hex=author_id_hex)
            return get_object_or_404(Author, id=author_id)
        except ValueError:
            raise ValueError("Invalid hexadecimal author_id")
    ## get the author's inbox    
    def get_inbox(self):
        try:
            author = self.get_author()
            return(get_object_or_404(Inbox, author=author))
        except ValueError:
            raise ValueError("Invalid hexadecimal author_id")

    
    def perform_create(self, serializer):
        validated_data = serializer.validated_data
        type = validated_data['type']
        type = type.lower()
        if type == 'like':
            author_url = validated_data['author']
            object_url = validated_data['object']
            if "post" in object_url:
                object_type = "post"
            # the author that is doing the liking
            author = Author.objects.get(url=author_url)
            if object_type == 'post':
                post = Post.objects.get(url=object_url)
                like = Like.objects.create(liked_post=post, author=author, object=object_url)
                like.save()

                inbox, created = Inbox.objects.get_or_create(author=self.get_author())
                inbox.likes.add(like)
    
   