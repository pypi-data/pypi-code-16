from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models
import json

#from his.models import MasterTrama

#@receiver(post_save, sender=models.Model)
@receiver(post_save)
def save_model(sender, **Kwargs):
	#import pdb;
	#pdb.set_trace()
	
	if hasattr(Kwargs['instance']._meta,'schemaTramaHis'):
		
		object_meta = Kwargs['instance']
		meta_dict = Kwargs['instance']._meta.schemaTramaHis
		object_meta.__class__.objects.generate(object_meta, meta_dict)

		


