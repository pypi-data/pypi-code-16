#!/usr/bin/python
# -*- coding: utf-8 -*-

import apiRequest

class syntaxdb():
    def __init__(self):
        self.api_request = apiRequest.Request()
        self.parameters = {}

    def pre_process(self):
        #convert option value to string(recommend pass value's type exactly like the API Doc)
        for i in self.parameters:
            if not isinstance(self.parameters[i], str):
                self.parameters[i] = str(self.parameters[i])

        self.api_request.reset_url()
        if 'language_permalink' in self.parameters:
            self.api_request.addPath('languages', self.parameters['language_permalink'])
            del(self.parameters['language_permalink'])
        if 'category_id' in self.parameters:
            self.api_request.addPath('categories', self.parameters['category_id'])
            del(self.parameters['category_id'])
        if 'concept_permalink' in self.parameters:
            self.api_request.addPath('concepts', self.parameters['concept_permalink'])
            del(self.parameters['concept_permalink'])
        if 'concept_id' in self.parameters:
            self.api_request.addPath('concepts', self.parameters['concept_id'])
            del(self.parameters['concept_id'])

    def category(self):
        self.pre_process()
        if 'categories' not in self.api_request.request_url:
            self.api_request.addPath('categories')
        if 'q' in self.parameters:
            self.api_request.addPath('search')
        if self.parameters:
            self.api_request.addOptions(self.parameters)
        return self.api_request.send_request()
        
    def concept(self):
        self.pre_process()
        if 'concepts' not in self.api_request.request_url:
            self.api_request.addPath('concepts')
        if 'q' in self.parameters:
            self.api_request.addPath('search')
        if self.parameters:
            self.api_request.addOptions(self.parameters)
        return self.api_request.send_request()

    def language(self):
        self.pre_process()
        if 'languages' not in self.api_request.request_url:
            self.api_request.addPath('languages')
        if 'q' in self.parameters:
            self.api_request.addPath('search')
        if self.parameters:
            self.api_request.addOptions(self.parameters)
        return self.api_request.send_request()