    def do_action(self, acs_request):
        ep = None
        if acs_request.get_location_service_code() is not None:
            ep = self.__location_service.find_product_domain(self.get_region_id(), acs_request.get_location_service_code())
        if ep is None:
            ep = region_provider.find_product_domain(self.get_region_id(), acs_request.get_product())
            if ep is None:
                raise exs.ClientException(error_code.SDK_INVALID_REGION_ID, error_msg.get_msg('SDK_INVALID_REGION_ID'))
            if not isinstance(acs_request, AcsRequest):
                raise exs.ClientException(error_code.SDK_INVALID_REQUEST, error_msg.get_msg('SDK_INVALID_REQUEST'))
        try:
            # style = acs_request.get_style()
            content = acs_request.get_content()
            method = acs_request.get_method()
            header = acs_request.get_signed_header(self.get_region_id(), self.get_access_key(),
                                                   self.get_access_secret())
            if self.get_user_agent() is not None:
                header['User-Agent'] = self.get_user_agent()
                header['x-sdk-client'] = 'python/2.0.0'
            protocol = acs_request.get_protocol_type()
            prefix = self.__replace_occupied_params(acs_request.get_domain_pattern(), acs_request.get_domain_params())
            url = acs_request.get_url(self.get_region_id(), self.get_access_key(), self.get_access_secret())
            if prefix is None:
                response = HttpResponse(ep, url, method, {} if header is None else header, protocol, content,
                                        self.__port)
            else:
                response = HttpResponse(prefix + ',' + ep, url, method, {} if header is None else header, protocol,
                                        content, self.__port)
            _header, _body = response.get_response()
            # if _body is None:
            # 	raise exs.ClientException(error_code.SDK_SERVER_UNREACHABLE, error_msg.get_msg('SDK_SERVER_UNREACHABLE'))
            return _body
        except IOError:
            raise exs.ClientException(error_code.SDK_SERVER_UNREACHABLE, error_msg.get_msg('SDK_SERVER_UNREACHABLE'))
        except AttributeError:
            raise exs.ClientException(error_code.SDK_INVALID_REQUEST, error_msg.get_msg('SDK_INVALID_REQUEST'))

