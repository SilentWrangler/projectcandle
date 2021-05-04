from django.forms import ModelForm
from .models import Post

class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['headline','content', 'reply_to', 'categories','last_edit_reason', 'frontpage']


def ReplyForm(OP):
    data = {
        'reply_to': OP,
        'categories': OP.categories,
        'headline':f'RE: {OP.headline}'
    }
    return PostForm(data)