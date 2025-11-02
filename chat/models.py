from django.db import models
from django.contrib.auth.models import User
from trader.models import Jobs

# The default messages model only
class Message(models.Model):
    job = models.ForeignKey(Jobs, on_delete=models.CASCADE, related_name='job_messages',null=True)
    sender = models.ForeignKey(User, related_name="sent_messages", on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name="received_messages", on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} -> {self.receiver}: {self.content[:20]}"

# Create your models here.
