from django.forms import ModelForm, HiddenInput, Textarea, TextInput
from .models import Post

class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['headline', 'content', 'reply_to', 'categories', 'last_edit_reason', 'frontpage']
        widgets = {
            'headline': TextInput(attrs={"class": "post-form big-input"}),
            'content': Textarea(attrs={"class": "post-form big-input"}),
        }
        labels = {
            "headline": "",
            "content": "",
            "frontpage": "Frontpage"
        }

class NonAdminPostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['headline', 'content', 'reply_to', 'categories']
        widgets = {
            'reply_to': HiddenInput(),
            'headline': TextInput(attrs={"class": "post-form big-input"}),
            'content': Textarea(attrs={"class": "post-form big-input"}),
        }

def ReplyForm(OP):
    data = {}

    data['reply_to']= OP
    data['categories']= OP.categories
    data['headline']=f'RE: {OP.headline}'

    return PostForm(data)

def NonAdminReply(OP):
    data = {}

    data['reply_to']= OP
    data['categories']= OP.categories
    data['headline']=f'RE: {OP.headline}'


    return NonAdminPostForm(data)