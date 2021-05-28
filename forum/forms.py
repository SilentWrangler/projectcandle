from django.forms import ModelForm, HiddenInput
from .models import Post

class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['headline','content', 'reply_to', 'categories','last_edit_reason', 'frontpage']

class NonAdminPostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['headline','content', 'reply_to', 'categories']
        widgets = {
            'reply_to': HiddenInput(),
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