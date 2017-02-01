# -*- coding: utf-8 -*-
import sys
from numbers import Number

from osxcollector.output_filters.summary_filters.summary import SummaryFilter


class HtmlSummaryFilter(SummaryFilter):
    """Prints the analysis summary (AKA "Very Readable Output") in HTML format."""

    def __init__(self, html_output_file=None, **kwargs):
        super(HtmlSummaryFilter, self).__init__(summary_output_file=html_output_file, **kwargs)

    def filter_line(self, blob):
        """Each Line of OSXCollector output will be passed to filter_line.

        The OutputFilter should return the line, either modified or unmodified.
        The OutputFilter can also choose to return nothing, effectively swallowing the line.

        Args:
            output_line: A dict

        Returns:
            A dict or None
        """
        if 'osxcollector_vthash' in blob:
            self._vthash.append(blob)

        if 'osxcollector_vtdomain' in blob:
            self._vtdomain.append(blob)

        if 'osxcollector_opendns' in blob:
            self._opendns.append(blob)

        if 'osxcollector_blacklist' in blob:
            self._blacklist.append(blob)

        if 'osxcollector_related' in blob:
            self._related.append(blob)

        if self._show_signature_chain:
            if 'signature_chain' in blob and blob['osxcollector_section'] in ['startup', 'kext']:
                signature_chain = blob['signature_chain']
                if not len(signature_chain) or 'Apple Root CA' != signature_chain[-1]:
                    self._signature_chain.append(blob)

        if self._show_browser_ext:
            if blob['osxcollector_section'] in ['firefox', 'chrome'] and blob.get('osxcollector_subsection') == 'extensions':
                self._extensions.append(blob)

        return blob

    def _write(self, text):
        try:
            self._output_stream.write(text.encode('utf-8', errors='replace'))
        except UnicodeDecodeError as err:
            self._output_stream.write(text)
            sys.stderr.write(
                'Unicode decode error when encoding text:\n{0}\nError:\n{1}\n'
                .format(text, err))

    def end_of_lines(self):
        """Called after all lines have been fed to filter_output_line.

        The OutputFilter can do any batch processing on that requires the complete input.

        Returns:
            An array of dicts (empty array if no lines remain)
        """
        self._write('''<html><head><style>
            body {
                color: #fff;
                background: #333;
                font-family:'Helvetica Neue', Helvetica, Arial, sans-serif;
            }

            h1, h2, h3 {
                color: #3cb52e;
                font-weight: bold;
            }

            p {
                color: #ccccc8;
            }

            a {
                color: #ff69b4;
            }

            a:hover {
                color: #00ff00;
            }

            .key {
                color: #999;
            }

            .val {
                color: #00ff00;
            }
        </style></head><body>''')
        self._print_header('Very Readable Output Bot')
        self._print_para('Let\'s see what\'s up with this machine.')

        self._print_header('Table of contents', level=2)
        self._write('<ul id="toc">')

        if len(self._vthash):
            self._print_section_link(
                "vthash", "VirusTotal bad hash hits", len(self._vthash))

        if len(self._vtdomain):
            self._print_section_link(
                "vtdomain", "VirusTotal bad domain hits", len(self._vtdomain))

        if len(self._opendns):
            self._print_section_link(
                "opendns", "OpenDNS Investigate hits", len(self._opendns))

        if len(self._blacklist):
            self._print_section_link(
                "blacklist", "Blacklist hits", len(self._blacklist))

        if len(self._related):
            self._print_section_link(
                "related", "Related hits", len(self._related))

        if len(self._signature_chain):
            self._print_section_link(
                "signature_chain", "Signature chain",
                len(self._signature_chain))

        if len(self._extensions):
            self._print_section_link(
                "extensions", "Extensions", len(self._extensions))

        if len(self._add_to_blacklist):
            self._print_section_link(
                "add_to_blacklist", "Blacklist update suggestions",
                len(self._add_to_blacklist))

        self._write('</ul>')

        if len(self._vthash):
            self._write('<div id="vthash">')
            self._print_header('VirusTotal bad hash hits', level=2)
            self._print_para('Dang! You\'ve got known malware on this machine. Hope it\'s commodity stuff')
            self._summarize_blobs(self._vthash)
            self._print_para('Sheesh! This is why we can\'t have nice things!')
            self._write('</div>')

        if len(self._vtdomain):
            self._write('<div id="vtdomain">')
            self._print_header('VirusTotal bad domain hits', level=2)
            self._print_para('I see you\'ve been visiting some \'questionable\' sites. If you trust VirusTotal that is.')
            self._summarize_blobs(self._vtdomain)
            self._print_para('I hope it was worth it!')
            self._write('</div>')

        if len(self._opendns):
            self._write('<div id="opendns">')
            self._print_header('OpenDNS Investigate hits', level=2)
            self._print_para('Well, here\'s some domains OpenDNS wouldn\'t recommend.')
            self._summarize_blobs(self._opendns)
            self._print_para('You know you shouldn\'t just click every link you see? #truth')
            self._write('</div>')

        if len(self._blacklist):
            self._write('<div id="blacklist">')
            self._print_header('Blacklist hits', level=2)
            self._print_para('We put stuff on a blacklist for a reason. Mostly so you don\'t do this.')
            self._summarize_blobs(self._blacklist)
            self._print_para('SMH')
            self._write('</div>')

        if len(self._related):
            self._write('<div id="related">')
            self._print_header('Related hits', level=2)
            self._print_para('This whole things started with just a few clues. Now look what I found.')
            self._summarize_blobs(self._related)
            self._print_para('Nothing hides from Very Readable Output Bot')
            self._write('</div>')

        if len(self._signature_chain):
            self._write('<div id="signature_chain">')
            self._print_header('Signature chain', level=2)
            self._print_para('If these binaries were signed by \'Apple Root CA\' I\'d trust them more.')
            self._summarize_blobs(self._signature_chain)
            self._print_para('Let\'s just try and stick with some safe software')
            self._write('</div>')

        if len(self._extensions):
            self._write('<div id="extensions">')
            self._print_header('Extensions', level=2)
            self._print_para('Let\'s see what\'s hiding in the browser, shall we.')
            self._summarize_blobs(self._extensions)
            self._print_para('You know these things have privileges galore.')
            self._write('</div>')

        if len(self._add_to_blacklist):
            self._write('<div id="add_to_blacklist">')
            self._add_to_blacklist = list(set(self._add_to_blacklist))
            self._print_header('Blacklist update suggestions', level=2)
            self._print_para('If I were you, I\'d probably update my blacklists to include:')
            for key, val in self._add_to_blacklist:
                self._summarize_val(key, val)
            self._print_para('That might just help things, Skippy!')
            self._write('</div>')

        self._print_para('Very Readable Output Bot')
        self._print_para('#kaythanksbye')

        self._write('</body></html>')

        return []

    def _print_section_link(self, section, title, size):
        self._write('<li><a href="#{0}">{1}</a> ({2})</li>'.format(
            section, title, size))

    def _summarize_blobs(self, blobs):
        self._write('<ol class="blobs">')
        for blob in blobs:
            self._write('<li>')
            self._summarize_line(blob)

            add_to_blacklist = False

            if 'osxcollector_vthash' in blob:
                self._summarize_vthash(blob)
                add_to_blacklist = True

            if 'osxcollector_vtdomain' in blob:
                self._summarize_vtdomain(blob)

            if 'osxcollector_opendns' in blob:
                self._summarize_opendns(blob)

            if 'osxcollector_blacklist' in blob:
                for key in blob['osxcollector_blacklist'].keys():
                    self._summarize_val(u'blacklist-{0}'.format(key), blob['osxcollector_blacklist'][key])

            if 'osxcollector_related' in blob:
                for key in blob['osxcollector_related'].keys():
                    self._summarize_val(u'related-{0}'.format(key), blob['osxcollector_related'][key])

            if 'md5' in blob and '' == blob['md5']:
                add_to_blacklist = True

            if add_to_blacklist:
                blacklists = blob.get('osxcollector_blacklist', {})
                values_on_blacklist = blacklists.get('hashes', [])
                for key in ['md5', 'sha1', 'sha2']:
                    val = blob.get(key, '')
                    if len(val) and val not in values_on_blacklist:
                        self._add_to_blacklist.append((key, val))

                values_on_blacklist = blacklists.get('domains', [])
                for domain in blob.get('osxcollector_domains', []):
                    if domain not in values_on_blacklist:
                        self._add_to_blacklist.append(('domain', domain))
            self._write('</ul>')  # this is the end of the list started by "_summarize_line"
            self._write('</li>')
        self._write('</ol>')

    def _summarize_line(self, blob):
        section = blob.get('osxcollector_section')
        subsection = blob.get('osxcollector_subsection', '')

        self._print_header(u'{0} {1}'.format(section, subsection), level=3)
        self._write('<ul class="list">')
        for key in sorted(blob.keys()):
            if not key.startswith('osxcollector') and blob.get(key):
                val = blob.get(key)
                self._summarize_val(key, val)

    def _summarize_vthash(self, blob):
        for blob in blob['osxcollector_vthash']:
            for key in ['positives', 'total', 'scan_date']:
                val = blob.get(key)
                self._summarize_val(key, val, 'vthash')
            permalink = blob.get('permalink')
            self._write(u'<li><a href="{0}" target="_blank">{0}</a></li>'.format(permalink))

    def _summarize_vtdomain(self, blob):
        for blob in blob['osxcollector_vtdomain']:
            for key in ['domain', 'detections']:
                val = blob.get(key)
                self._summarize_val(key, val, 'vtdomain')

    def _summarize_opendns(self, blob):
        for blob in blob['osxcollector_opendns']:
            for key in ['domain', 'categorization', 'security']:
                val = blob.get(key)
                self._summarize_val(key, val, 'opendns')
            link = blob.get('link')
            self._write(u'<li><a href="{0}" target="_blank">{0}</a></li>'.format(link))

    def _summarize_val(self, key, val, prefix=None):
        self._write('<li>')
        self._print_key(key, prefix)
        self._print_val(val)
        self._write('</li>')

    def _print_header(self, text, level=1):
        self._write(u'<h{0}>{1}</h{0}>'.format(level, text))

    def _print_para(self, text):
        self._write(u'<p>{0}</p>'.format(text))

    def _print_list_item(self, item):
        self._write('<li>')
        self._print_val(item)
        self._write('</li>')

    def _print_key(self, key, prefix=None):
        if not prefix:
            prefix = ''
        else:
            prefix += '-'

        self._write(u'<span class="key">{0}{1}</span>: '.format(prefix, key))

    def _print_val(self, val):
        if isinstance(val, list):
            self._write('<ul class="list">')
            for v in val:
                self._print_list_item(v)
            self._write('</ul>')
        elif isinstance(val, dict):
            self._write('<ul class="dict">')
            keys = val.keys()
            for key in keys:
                self._summarize_val(key, val[key])
            self._write('</ul>')
        elif isinstance(val, Number):
            val = str(val)
            self._encode_val(val)
        elif isinstance(val, basestring):
            self._encode_val(val)

    def _encode_val(self, val):
        if not isinstance(val, unicode):
            val = unicode(val, errors='replace')

        self._write(u'<span class="val">{0}</span>'.format(val))
