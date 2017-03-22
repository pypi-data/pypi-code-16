# parse a raw text file into a dictionary of dictionaries
# headers is a list of dictionaries, with members: { header: header_text, type: vars, block }
from operator import itemgetter
import os
import json
import re

# parser definitions
HEADER_DEF = [
    {'header_text': 'headers', 'type': 'vars'},
    {'header_text': 'js_base', 'type': 'block'}
]

SOURCE_DEF = [
    {'header_text': 'headers', 'type': 'vars'},
    {'header_text': 'js', 'type': 'block'},
    {'header_text': 'css', 'type': 'block'},
    {'header_text': 'html', 'type': 'block'}
]


class YaffParser(object):
    def __init__(self, raw_text, headers=None):
        self.raw_text = raw_text
        self.headers = headers or []
        self.output = {}
    
    def parse_markup(self):

        out_dic = {}
        sections = []

        # go through text and find the start
        for h in self.headers:
            header = h['header_text']
            h_start = self.raw_text.find('[' + header + ']')
            h['start'] = h_start

        # sort headers by start
        headers_sorted = sorted(self.headers, key=itemgetter('start'))

        # go through headers and create section dictionaries
        l = len(headers_sorted)
        i = 0
        while i < l:
            h = headers_sorted[i]
            header = h['header_text']
            h_start = h['start']
            h_len = len(header)

            if i + 1 < l:
                section_end = headers_sorted[i+1]['start'] - 1
            else:
                section_end = len(self.raw_text)

            section_dic = {'header': header, 'start': h_start + h_len + 2, 'end': section_end, 'type': h['type']}
            sections.append(section_dic)
            i += 1

        # parse each section, producing a dictionary with of format {var: value} if type==vars, {body: body} if type== body.
        # Append to out_dic
        for section in sections:

            raw_body = self.raw_text[section['start']:section['end']].strip()
            item_dic = {}

            if section['type'] == 'vars':

                raw_lines = raw_body.split('\n')

                for line in raw_lines:
                    line_split = line.split('=')
                    item_dic[line_split[0].strip()] = line_split[1].strip()

            elif section['type'] == 'block':

                item_dic = {'body': raw_body}

            out_dic[section['header']] = item_dic

        self.output = out_dic


class YaffProject(object):
    """
    Object representing an entire Yaff Project


    """
    def __init__(self, source_path, target_path, process_flags):
        self.source_path = source_path
        self.target_path = target_path
        self.process_flags = process_flags
        self.source_files = []
        self.template_files = []
        self.target_filenames = {}
        self.header_file = ""
        self.headers = {}
        self.components = []
        self.templates = []
        self.selector_class_map = {}
        self.component_path = os.path.join(self.source_path, 'components')
        self.template_path = os.path.join(self.source_path, 'templates')
        
    def get_source_file_list(self):

        self.source_files = [f for f in os.listdir(self.component_path) if os.path.isfile(os.path.join(self.component_path, f))
                and os.path.splitext(f)[1] == '.ycf']

        for f in os.listdir(self.source_path):
            if os.path.isfile(os.path.join(self.source_path, f)) and f == 'header.ypf':
                self.header_file = f
                break
        else:
            self.header_file = None

        self.template_files = [f for f in os.listdir(self.template_path) if os.path.isfile(os.path.join(self.template_path, f))]
            
    def parse_header_file(self):
        with open(os.path.join(self.source_path, self.header_file), 'r') as f:
            headers_raw = f.read()

        parser = YaffParser(headers_raw, HEADER_DEF)
        parser.parse_markup()
        self.headers = parser.output
        
    def get_sources(self):
        self.components = []
        for source_file in self.source_files:
            print "Getting source file " + os.path.join(self.component_path, source_file)
            component = YaffComponent(source_file, self.process_flags, self.headers['headers']['namespace'],
                                      self.component_path)
            self.components.append(component)
            self.selector_class_map[component.selector] = component.js_class
            print "Source file " + os.path.join(self.component_path, source_file) + " loaded successfully"

        for template_file in self.template_files:
            target_filename = self.headers['headers']['project_name'] + '_' + self.headers['headers']['API_version'] \
                              + '.html'
            template = YaffTemplate(os.path.join(self.template_path, template_file), target_filename, self.components)
            template.parse_template()
            self.templates.append(template)

    def write_target_files(self):
        for key, value in self.process_flags.iteritems():
            if value and key == 'templates':
                self.write_templates()
            elif value:
                self.write_target_file(key)
    
    def write_target_file(self, target_type):

        print "Processing " + target_type + " file "

        target_path = os.path.join(self.target_path, target_type)
        if not os.path.exists(target_path):
            os.makedirs(target_path)

        if target_type == 'css':
            target_filename = self.headers['headers']['project_name'] + '_' + self.headers['headers'][
                'API_version'] + '.' + self.headers['headers']['css_extension']
        else:
            target_filename = self.headers['headers']['project_name'] + '_' + self.headers['headers']['API_version'] + '.' + target_type

        target_file = open(os.path.join(target_path, target_filename), 'w')

        if target_type == "js":
            js_base = self.headers['js_base']['body'].replace('{namespace}', self.headers['headers']['namespace'])
            js_base = js_base.replace('{API_version}', self.headers['headers']['API_version'])
            js_base = js_base.replace('{selector_class_map}', str(self.selector_class_map))
            target_file.write(js_base)

            # copy yaff.js base file to target
            yaff_base_source = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'yaff.js'), 'r').read()
            yaff_base_target = open(os.path.join(target_path, 'yaff.js'), 'w')
            yaff_base_target.write(yaff_base_source)
            yaff_base_target.close()

        elif target_type == 'css':
            css_base = "@import 'scss_base';\n\n"
            target_file.write(css_base)

            # copy scss base file to target
            scss_base_source = open(os.path.join(self.source_path, '_scss_base.scss'), 'r').read()
            scss_base_target = open(os.path.join(target_path, '_scss_base.scss'), 'w')
            scss_base_target.write(scss_base_source)
            scss_base_target.close()

        # write output for each component
        for component in self.components:
            output = component.output.get(target_type)
            if output is not None:
                target_file.write(output)
        
        # close js_target file
        target_file.close()

        print target_filename + " written."

    def write_templates(self):
        target_path = os.path.join(self.target_path, 'html')
        if not os.path.exists(target_path):
            os.makedirs(target_path)

        for t in self.templates:
            print "Processing template from " + t.source_file
            target_filename = os.path.basename(t.source_file)
            target_file = open(os.path.join(target_path, target_filename), 'w')
            target_file.write(t.template_output)
            target_file.close()
            print "Template file " + os.path.join(target_path, target_filename) + " written."


class YaffComponent(object):
    """
    Object representing a Yaff component. Accepts:
    
    """
    def __init__(self, source_file, process_flags, namespace, source_path="/"):
        self.source_path = source_path
        self.source_file = source_file
        self.process_flags = process_flags
        self.namespace = namespace
        self.source = {}
        self.output = {"js": "", "html": "", "css": ""}
        
        self.js_class = ""
        self.selector = ""
                               
        self.parse_source_file()
        
        for key, value in self.process_flags.iteritems():
            if value:
                self.compile_output(key)
        
    def parse_source_file(self):
        with open(os.path.join(self.source_path, self.source_file), 'r') as f:
            source_raw = f.read()

        parser = YaffParser(source_raw, SOURCE_DEF)
        parser.parse_markup()
        self.source = parser.output
        
        self.js_class = self.source['headers']['class']
        self.selector = self.source['headers']['selector']
        
    def compile_output(self, output_type):
       
        if output_type == 'js':
            self.output["js"] =  "\n\n/*******************************\n**  " + self.source['headers']['name'] + "\n**  " + \
                self.source['headers']['description'] + "\n*******************************/\n\n" \
                + self.namespace + "." + self.source['headers']['class'] + " = " \
                + self.source['headers']['extends'] + ".extend(" + self.source['js']['body'] + ");"
            
        elif output_type == 'html':
            self.output["html"] = "\n\n{# " + self.source['headers']['name'] + " #}\n" \
                + "{# " + self.source['headers']['description'] + " #}\n\n" \
                + "{%- macro " + self.source['headers']['macro_name'] + "(data) -%}\n" \
                + self.source['html']['body'] + "\n" + "{%- endmacro -%}"
        elif output_type == 'css':
            self.output["css"] = self.source['css']['body'] + "\n\n"


class YaffTemplate(object):
    def __init__(self, source_file, macro_filename, components):
        self.source_file = source_file
        self.template_source = open(source_file).read()
        self.macro_filename = macro_filename
        self.components = components
        self.template_components = []
        self.template_output = self.template_source
        self.import_statement = "{% import 'html/" + self.macro_filename + "' as yaff_macros %}\n\n"

    def parse_template(self):
        self.template_output = self.import_statement + self.template_output

        # keep searching/compiling until no more components are left uncompiled
        # allows nesting of components within others

        while True:
            processed_count = 0

            # find each component
            for component in self.components:
                regex = '(<' + component.source['headers']['html_tag'] + ')([\s\S]*?)(>)([\s\S]*?)(<\/' + \
                        component.source['headers']['html_tag'] + '>)'
                # keep looking for new components until no more to be found
                while True:
                    m = re.search(regex, self.template_output)

                    # if expression not found, go to the next component
                    if m is None:
                        break

                    processed_count += 1
                    print 'instance of ' + component.source['headers']['html_tag'] + ' found'
                    # parse the attributes
                    attr_re = '(\S+?)(=)"(.+?)"'
                    attrs = {}
                    for a in re.finditer(attr_re, m.group(2)):
                        attrs[a.group(1)] = a.group(3)

                    # build the string to replace the original tags with
                    macro_name = "yaff_macros." + component.source['headers']['macro_name']
                    output_string = "{{%- set data={} -%}} \n{{% call {}(data) %}}{}{{% endcall %}}".format(json.dumps(attrs), macro_name, m.group(4))

                    # replace the original tags
                    self.template_output = self.template_output[:m.start()] + output_string + self.template_output[m.end():]

            if processed_count == 0:
                break
