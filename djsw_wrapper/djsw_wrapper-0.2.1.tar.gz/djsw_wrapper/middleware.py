from django.utils.deprecation import MiddlewareMixin

class SwaggerMiddleware(MiddlewareMixin):
	def process_request(self, request):
		print(request)

		#return None