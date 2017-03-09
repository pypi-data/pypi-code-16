# -*- coding: utf-8 -*-
# copyright 2016 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""elasticsearch search views"""
from six import text_type as unicode

from elasticsearch.exceptions import NotFoundError
from elasticsearch_dsl import FacetedSearch, TermsFacet, DateHistogramFacet
from bs4 import BeautifulSoup

from logilab.mtconverter import xml_escape

import cwtags.tag as t
from cubicweb import _
from cubicweb.view import StartupView

from cubes.elasticsearch.es import indexable_types, get_connection
from cubes.elasticsearch.search_helpers import compose_search


class CWFacetedSearch(FacetedSearch):
    # fields that should be searched
    fields = ["title^3", "description^2", '_all']

    facets = {
        # use bucket aggregations to define facets
        'cw_etype': TermsFacet(field='cw_etype'),
        'creation_date': DateHistogramFacet(field='creation_date', interval='month'),
    }

    def __init__(self, query=None,
                 filters={},
                 doc_types=None,
                 index=None,
                 parents_for=None,
                 children_for=None,
                 form=None,
                 **kwargs):
        if index:
            self.index = index
        if doc_types:
            self.doc_types = doc_types
        if form:
            self.form = form
        else:
            self.form = {}
        self.parents_for = parents_for
        self.children_for = children_for
        self.extra_kwargs = kwargs
        super(CWFacetedSearch, self).__init__(query, filters)

    def query(self, search, query):
        if query:
            common = 'debug-es-disable-common' not in self.form  # default True
            phrase = 'debug-es-disable-phrase' not in self.form  # default True
            fuzzy = 'fuzzy' in self.form  # default False
            return compose_search(search,
                                  query=query,
                                  fields=self.fields,
                                  fuzzy=fuzzy,
                                  common=common,
                                  phrase=phrase,
                                  parents_for=self.parents_for,
                                  children_for=self.children_for)
        return search

    def highlight(self, search):
        """
        Add custom highlighting
        """
        search = search.highlight(*(f if '^' not in f else f.split('^', 1)[0] for f in self.fields))
        return search.highlight_options(pre_tags="",
                                        post_tags="",
                                        fragment_size=150)


class ElasticSearchView(StartupView):
    __regid__ = "esearch"
    previous_link = u' &lt; '
    next_link = u' &gt; '
    middle_link = u" &middot; " * 3
    title = _('Search')

    def render_search_comp(self):
        search_comp = self._cw.vreg['components'].select_or_none('search-comp',
                                                                 self._cw)
        if search_comp:
            search_comp.render(w=self.w)

    def do_search(self, query_string):
        get_connection(self._cw.vreg.config)
        facet_selections = {}
        start, stop = 0, 10
        parents_for = children_for = None
        for key, value in self._cw.form.items():
            if key.startswith('es_'):
                # FIXME TODO have better typing mechanisme (inspect facets?)
                try:
                    facet_selections[key.replace('es_', '')] = int(value)
                except ValueError:
                    facet_selections[key.replace('es_', '')] = value
            if key == 'parents_for':
                parents_for = value
            if key == 'children_for':
                children_for = value
            if key == 'page':
                start = (max(int(value) - 1, 0)) * 10
                stop = start + 10
        search = self.customize_search(query_string,
                                       facet_selections,
                                       start, stop,
                                       parents_for=parents_for,
                                       children_for=children_for)
        if 'debug-es' in self._cw.form:
            import json
            self.w(u'<pre>')
            self.w(unicode(json.dumps(search._s.to_dict(), indent=2)))
            self.w(u'</pre>')
            self.w(u'<br/>')
        try:
            response = search.execute()
            if 'debug-es' in self._cw.form:
                import json
                self.w(u'<pre>')
                self.w(unicode(json.dumps(response.to_dict(), indent=2)))
                self.w(u'</pre>')
                self.w(u'<br/>')
            return response
        except NotFoundError:
            self.w(u'index not found in elasticsearch')
            return

    def call(self, **kwargs):
        # TODO if no ES configuration, redirect or display warning
        self.render_search_comp()
        query_string = self._cw.form.get('q', self._cw.form.get('search', ''))
        self.w(u'<h1>%s</h1>' % self._cw._(self.title))
        response = self.do_search(query_string)
        if response.hits.total:
            self.w(u'<h2>Resultats pour : <em>%s</em></h2>' %
                   xml_escape(query_string))
            self.w(u'Resultats: %s' % response.hits.total)
            if hasattr(response, 'facets'):
                self.display_facets(response)
        self.display_results(response)

    def customize_search(self, query_string, facet_selections,
                         start=0, stop=10, **kwargs):
        '''
        This is where one can customize the search by modifying the
        query string and facet selection in an inherited class.

        For example :
        * add specific keywords sur as id:text and
          add them the facet_selection
        * use your own CWFacetedSearch class to modify fields
          and facets
        '''
        indexable = indexable_types(self._cw.vreg.schema)
        return CWFacetedSearch(query_string,
                               facet_selections,
                               index=self._cw.vreg.config.get('index-name'),
                               doc_types=indexable,
                               form=self._cw.form,
                               **kwargs)[start:stop]

    def display_results(self, response):
        '''
        Display results obtained from elasticsearch
        '''
        self.w(u'<div id="main-center" class="col-xs-10" role="main">')
        self.pagination(response)
        self.w(u'<ul>')
        for result in response:
            self.w(u'<li>')
            infos = result.to_dict()
            infos['_score'] = result.meta.score
            infos['keys'] = result.to_dict().keys()
            infos['url'] = infos['cwuri'].startswith(
                '_auto_generated') and infos['eid'] or infos['cwuri']
            self.customize_infos(infos)
            try:
                self.w(
                    u'<a href="%(url)s">%(title)s</a> (%(_score).2f)<br/>' % (infos))
                if self._cw.form.get('debug-es'):
                    self.w(u' [%(keys)s] <br/>' % infos)
            except KeyError:
                self.w(u'Missing key in : %s' % infos.keys())
            try:
                for fragment in result.meta.highlight.content:
                    self.w(u'... %s' %
                           BeautifulSoup(fragment, 'lxml').get_text())
                    self.w(u' ... <br/>')
            except AttributeError:
                pass
            self.w(u'</li>')
        self.w(u'</ul>')
        self.pagination(response)
        self.w(u'</div>')

    def customize_infos(self, infos):
        '''
        This is where one can customize the infos being displayed

        For example : set the title according to your rules and data set
        '''
        pass

    def pagination(self, response):
        '''
        Pagination HTML generation
        '''
        if response.hits.total <= 10:
            return
        url_params = self._cw.form.copy()
        with t.ul(self.w, klass="pagination") as ul:
            current_page = int(url_params.get('page', 1))
            url_params['page'] = current_page - 1
            if current_page - 1 >= 1:
                ul(t.li(t.a(self.previous_link,
                            href=xml_escape(self._cw.build_url(**url_params)))))
            else:
                ul(t.li(t.a(self.previous_link)))
            total_pages = min((response.hits.total / 10) + 2, 1000)
            page_padding = 3

            if current_page > page_padding:
                for page in range(1,
                                  min(page_padding + 1,
                                      current_page - page_padding)):
                    self.page_number(url_params, page, current_page, ul)
                if current_page > (page_padding * 2) + 1:
                    ul(t.li(t.a(self.middle_link)))
            for page in range(max(1, current_page - page_padding),
                              min(current_page + page_padding, total_pages)):
                self.page_number(url_params, page, current_page, ul)
            if current_page < total_pages - page_padding:
                if current_page < total_pages - page_padding * 2:
                    ul(t.li(t.a(self.middle_link)))
                for page in range(max(current_page + page_padding,
                                      total_pages - page_padding),
                                  total_pages):
                    self.page_number(url_params, page, current_page, ul)

            url_params['page'] = current_page + 1
            if current_page + 1 >= (total_pages):
                ul(t.li(t.a(self.next_link)))
            else:
                ul(t.li(t.a(self.next_link,
                            href=xml_escape(self._cw.build_url(**url_params)))))

    def page_number(self, url_params, page, current_page, ul):
        '''
        Generate HTML for page number (bold if page is current_page)
        '''
        url_params['page'] = page
        url = self._cw.build_url(**url_params)
        if page == current_page:
            ul(t.li(t.a(t.b(page),
                        href=xml_escape(url)),
               Class="active",))
        else:
            ul(t.li(t.a(page,
                        href=xml_escape(url))))
        return url

    @property
    def facets_to_display(self):
        '''
        Method to list facets to display (can be customized)
        '''
        return ('cw_etype', )

    def display_facets(self, response):
        '''
        Generate HTML for facets
        '''
        self.w(u'''<aside id="aside-main-left" class="col-xs-2 cwjs-aside">
                   <div class="panel panel-default contextFreeBox facet_filterbox">
                      <div class="panel-heading">
                         <div class="panel-title">Facettes</div>
                      </div>
        ''')
        for attribute in self.facets_to_display:
            url_params = self._cw.form.copy()
            if 'page' in url_params:
                del url_params['page']
            self.w(u'<div class="facetBody vocabularyFacet">')
            self.w(u'<div class="facetTitle">{}</div>'.format(attribute))
            for (tag, count, selected) in response.facets[attribute]:
                # facetValueSelected / facetValueDisabled in class
                facet_item = u'<div class="facetValue facetCheckBox">' \
                             '    <span>' \
                             '      <a href="{}">{} {}</a>' \
                             '    </span>' \
                             '</div>'
                if url_params.get('es_{}'.format(attribute)) != tag:
                    url_params['es_{}'.format(attribute)] = str(tag)
                else:
                    del url_params['es_{}'.format(attribute)]
                url = self._cw.build_url(**url_params)
                content = selected and '<div class="facet-active">{}</div>'.format(tag) or tag
                self.w(facet_item.format(url,
                                         content,
                                         count))
            self.w(u'</div>')
        self.w(u'</div></aside>')
