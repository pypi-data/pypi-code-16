import plotly.offline as po
import plotly.graph_objs as go
import os.path as op
from os import makedirs
from jinja2 import Environment, FileSystemLoader
from distutils.dir_util import copy_tree


class ReportGenerator:
    """This class contains all the methods used to report the results of a given
    run of primers generation

    Parameters:
    -----------
    report_template_folder: String
                            path to the folder with the HTML templates

    pparis: python dict(pair_id: ProbePair)
            probes pairs to be reported

    targets_records: python dict(seq_id: SeqRecord)
                     Target sequences

    report_dir: String
                Path to the folder where the report will be saved

    figures_dir: String
                 Path to the folder where the figures will be stored

    args: ArgParse object
          List of arguments used to run the program

    n_raw_probes: Integer
                  Total number of Probes generated

    pb_filtered: Python dict(String: Integer)
                 Probe filtering resume

    n_total_pairs: Integer
                   Total number of probe pairs generated

    pp_filtered: Python dict(String: Integer)
                 Probe pairs filtering resume
    """

    def __init__(self, args, primers_set, targets_records):

        # get the path of this file
        path = op.realpath(__file__)
        main_path = op.dirname(op.dirname(path))

        # from this path, reach the templates folder
        self.report_template_folder = op.join(main_path,
                                              "templates")
        self.ppairs = primers_set.probes_pairs
        self.targets_records = targets_records
        self.report_dir = op.join(args.output_prefix, "_site")
        self.figures_dir = op.join(self.report_dir, "figures")
        self.args = args

        # probes information
        self.n_raw_probes = primers_set.n_raw_probes
        self.pb_filtered = primers_set.pb_filtered

        # primers pair information
        self.n_total_pairs = primers_set.n_total_pairs
        self.pp_filtered = primers_set.pp_filtered

        if not op.exists(self.report_dir):
            makedirs(self.report_dir)

        if not op.exists(self.figures_dir):
            makedirs(self.figures_dir)

        copy_tree(op.join(self.report_template_folder, "site_libs"),
                  op.join(self.report_dir, "site_libs"))

    def generate_report(self):
        """ Generate all the HTML reports (settings, primers and primers pairs)

        Returns:
        Files: it generates a set of 3 HTML files, one reporting the primers
        settings, other reporting the primers statistincs and other reporting
        the primers pairs statistics

        Notes:
        It calls three differents functions to generate each HTNL report,
        generate_settings_report, generate_pairs_report and
        generate_primers_report
        """

        settings_html = self.generate_settings_report()
        handler = open(op.join(self.report_dir, "index.html"), "w")
        handler.write(settings_html)
        pairs_html = self.generate_pairs_report()
        handler = open(op.join(self.report_dir, "pairs.html"), "w")
        handler.write(pairs_html)
        primers_html = self.generate_primers_report()
        handler = open(op.join(self.report_dir, "primers.html"), "w")
        handler.write(primers_html)

    def generate_settings_report(self):

        """ Generates a HTML report with the settings of the run
        """

        env = Environment(loader=FileSystemLoader(self.report_template_folder))
        template = env.get_template("index.html")

        thermo = []
        filt = []
        pairing = []
        output = []
        info_sets = []

        targets = [record.id for record in self.targets_records]
        universe_file = op.basename(self.args.fasta_indx)
        output_name = self.args.output_prefix

        thermo_info = [["NaCl contentration:", str(self.args.na)+" M"],
                       ["Mg concentration:", str(self.args.mg)+" M"],
                       ["Operation temperature:",
                        str(int(self.args.op_temp))+" C"],
                       ["SDSS threshold:", str(self.args.sdss)],
                       ["Primer concentration:", str(self.args.prim_con)+" M"]]

        for pos in range(1, len(thermo_info)+1):
            if pos % 2 == 0:
                row = "even"
            else:
                row = "odd"
            thermo.append(dict(tr_class=row,
                               parameter=thermo_info[pos-1][0],
                               value=thermo_info[pos-1][1]))

        filt_info = [["Minimum primer size:",
                      str(self.args.min_prim_size)+" bp"],
                     ["Maximum primer size:",
                      str(self.args.max_prim_size)+" bp"],
                     ["Minimum local composition complexity:",
                      str(self.args.lcc)],
                     ["Minimum GC percentage:",
                      str(int(self.args.min_gc))+"%"],
                     ["Maximum GC percentage:",
                      str(int(self.args.max_gc))+"%"],
                     ["Minimum melting temperature:",
                      str(int(self.args.min_melt))+" C"],
                     ["Maximum melting temperature:",
                      str(int(self.args.max_melt))+" C"],
                     ["Minimum energy for hairpin formation:",
                      str(self.args.dgss)+" kcal/mol"],
                     ["Minimum energy for homodimer formation:",
                      str(self.args.dghm)+" kcal/mol"]]

        for pos in range(1, len(filt_info)+1):
            if pos % 2 == 0:
                row = "even"
            else:
                row = "odd"
            filt.append(dict(tr_class=row,
                             parameter=filt_info[pos-1][0],
                             value=filt_info[pos-1][1]))

        pairing_info = [["Edit distance for primer alignment:",
                         str(self.args.edit_distance)],
                        ["Minimum amplicon size:",
                         str(self.args.min_amp_size)+" bp"],
                        ["Maximum amplicon size:",
                         str(self.args.max_amp_size)+" bp"],
                        ["Minimum energy for heterodimer formation:",
                         str(self.args.ppdghm)+" kcal/mol"],
                        ["Minimum target fraction to be detected:",
                         str(self.args.target_frac)]]

        for pos in range(1, len(pairing_info)+1):
            if pos % 2 == 0:
                row = "even"
            else:
                row = "odd"
            pairing.append(dict(tr_class=row,
                                parameter=pairing_info[pos-1][0],
                                value=pairing_info[pos-1][1]))

        output_info = [["Maximum number of primers pairs reported:",
                        str(self.args.records)],
                       ["Primers prefix:", self.args.primers_prefix]]

        for pos in range(1, len(output_info)+1):
            if pos % 2 == 0:
                row = "even"
            else:
                row = "odd"
            output.append(dict(tr_class=row,
                               parameter=output_info[pos-1][0],
                               value=output_info[pos-1][1]))

        info_sets.append(dict(id="thermodynamic-settings",
                              name="Thermodynamic settings",
                              info=thermo))
        info_sets.append(dict(id="primers-filtering",
                              name="Primers filtering settings",
                              info=filt))
        info_sets.append(dict(id="primers-pairing",
                              name="Primers pairing settings",
                              info=pairing))
        info_sets.append(dict(id="output-options",
                              name="Output settings",
                              info=output))

        items = dict(output_name=output_name,
                     universe_file=universe_file,
                     targets=targets,
                     info_sets=info_sets)

        html_out = template.render(items)
        return html_out

    def generate_pairs_report(self):

        """ Generate a HTML report of the primers pairs
        """

        env = Environment(loader=FileSystemLoader(self.report_template_folder))
        template = env.get_template("pairs.html")
        pairs_res = []
        pairs_info = []
        output_name = self.args.output_prefix

        tmp_res = [["Total number of primers pairs generated:",
                    str(self.n_total_pairs)],
                   ["Pairs filtered because they don't detect" +
                    " the minimum fraction of targets:",
                    str(self.pp_filtered["frac"])],
                   ["Pairs filtered because they generate weird amplicons:",
                    str(self.pp_filtered["amp"])],
                   ["Pairs filtered because they interact one each other:",
                    str(self.pp_filtered["int"])],
                   ["Total pairs kept:",
                    str(self.pp_filtered["keep"])],
                   ["Total pairs reported:",
                    str(self.args.records)]]

        for row in tmp_res:
            pairs_res.append(dict(parameter=row[0], value=row[1]))

        flag = 0

        # iterate over each pair of primers
        for pair in self.ppairs:
            pa = pair.a
            pb = pair.b

            if flag == 0:
                display = "block"
                flag += 1
            else:
                display = "none"

            tmp_pair = dict(id=pair.id, a=pa.id, b=pb.id,
                            mean_amplicon=str(int(pair.mean_amp_len)),
                            inter_energy=pair.inter_energy,
                            melt_diff=pair.met_diff,
                            display=display,
                            figures=[])

            # iterate over each target
            for record in self.targets_records:

                # get alignments of each primer in the pair
                pa_algs = pa.get_alignments(record.id)
                pb_algs = pb.get_alignments(record.id)

                # if the aligments meet the amplicon criteria, retrieve
                # coordinates
                if len(pa_algs) != 0 and len(pb_algs) != 0:
                    pa_desc = (pa.id,) + pa_algs[0][:3]
                    pb_desc = (pb.id,) + pb_algs[0][:3]
                else:
                    pa_desc = None
                    pb_desc = None

                # define the name and path of the output html plot
                output_html = op.join(self.figures_dir,
                                      pair.id+"_"+record.id+".html")
                # draw the figures
                self.draw_primers(pa_desc, pb_desc, len(record), output_html)

                tmp_figure = dict(target=record.id,
                                  path=op.join("figures",
                                               op.basename(output_html)))
                tmp_pair["figures"].append(tmp_figure)

            pairs_info.append(tmp_pair)
        items = dict(pairs_info=pairs_info,
                     pairs_res=pairs_res,
                     output_name=output_name)
        html_out = template.render(items)
        return html_out

    def draw_primers(self, pa_desc, pb_desc, seq_len, output_file):
        """Draws a pair of primers over a given sequence
        Args:
        -----
        pa_desc: List(pb_id, start_seq, end_seq, strand)
                 Description of A primer. The description list stands for
                 Sequence ID and start and end positions of the primer over the
                 sequence

        pb_desc: List(pb_id, start_seq, end_seq, strand)
                 Description of B primer. Same as A primer

        seq_len: Integer
                 Length of the sequence where the primers will be drawn on

        output_file: String
                     Path to the HTML output generate for the image

        Returns:
        --------
            String: path to the HTML file
        """

        plt_width = seq_len
        plt_height = plt_width*0.35

        arrow_height = plt_height*0.45

        layout = {

                'xaxis': {
                            'range': [1, plt_width],
                            'zeroline': False,
                            'showline': True
                        },
                'yaxis': {
                            'range': [0, plt_height],
                            'showgrid': False,
                            'zeroline': False,
                            'showline': False,
                            'autotick': True,
                            'ticks': '',
                            'showticklabels': False
                        },
                'shapes': [],
                'margin': {
                    'l': 30,
                    'r': 30,
                    'b': 30,
                    't': 10
                }
        }

        # draw primers if they have coordinates in the target
        if pa_desc is not None and pb_desc is not None:
            a_path = self.get_svg_path(pa_desc, arrow_height)
            b_path = self.get_svg_path(pb_desc, arrow_height)
            layout["shapes"].append(
                            {
                             'type': 'path',
                             'path': a_path,
                             'fillcolor': 'rgba(255, 140, 184, 0.5)',
                             'line': {'color': 'rgb(255, 140, 184)'}
                            })
            layout["shapes"].append(
                            {
                             'type': 'path',
                             'path': b_path,
                             'fillcolor': 'rgba(57,160,255, 0.5)',
                             'line': {'color': 'rgb(22,76,193)'}
                            })

        if pa_desc[3] == "+" and pb_desc[3] == "-":
            x0 = pa_desc[2]
            x1 = pb_desc[1]
        else:
            x0 = pb_desc[2]
            x1 = pa_desc[1]
        y0 = arrow_height/2
        y1 = y0

        # add horizontal line between primers
        layout["shapes"].append({
            'type': 'line',
            'x0': x0,
            'y0': y0,
            'x1': x1,
            'y1': y1,
            'line': {
                'color': 'rgb(192, 192, 192)',
                'width': 2,
                'dash': 'dot',
            }
        })

        if pa_desc[3] == "+" and pb_desc[3] == "-":
            a_lab_x_pos = pa_desc[1]
            b_lab_x_pos = pb_desc[2]
            amp_len = pb_desc[2] - pa_desc[1] + 1
            amp_len_pos = a_lab_x_pos + amp_len/2 - 1
        else:
            b_lab_x_pos = pb_desc[1]
            a_lab_x_pos = pa_desc[2]
            amp_len = pa_desc[2] - pb_desc[1] + 1
            amp_len_pos = b_lab_x_pos + amp_len/2 + 1

        trace0 = go.Scatter(
                x=[a_lab_x_pos, b_lab_x_pos, amp_len_pos],
                y=[arrow_height*1.2, arrow_height*1.2, (arrow_height/2)*1.3],
                text=[pa_desc[0],
                      pb_desc[0],
                      "amp size: "+str(amp_len)],
                mode='text',
                hoverinfo='none'
        )

        data = [trace0]
        fig = {
                'data': data,
                'layout': layout,
        }
        url = po.plot(fig, filename=output_file, auto_open=False)

        # just a tweak to remove unnecessary buttons from plotly
        with open(url.replace('file://', ''), 'r') as file:

            tempHTML = file.read()
            # Replace the target strings
            tempHTML = tempHTML.replace('displaylogo:!0', 'displaylogo:!1')
            tempHTML = tempHTML.replace('modeBarButtonsToRemove:[]',
                                        'modeBarButtonsToRemove:["' +
                                        'sendDataToCloud", "pan2d",' +
                                        ' "select2d", "lasso2d",' +
                                        ' "hoverClosestCartesian", ' +
                                        '"hoverCompareCartesian"]')
            tempHTML = tempHTML.replace('"linkText": "Export to plot.ly",' +
                                        ' "showLink": true',
                                        '"linkText": "", "showLink": false')

        with open(url.replace('file://', ''), 'w') as file:
            file.write(tempHTML)
        del tempHTML

        return url

    def get_svg_path(self, p_desc, arrow_height):
        """ Generates an SVG description for a given primer

        Args:
        -----
        p_desc: List(pb_id, start_seq, end_seq, strand)
                 Description of A primer. The description list stands for
                 Sequence ID and start and end positions of the primer over the
                 sequence

        arrow_height: Float
                      Height of the primer draw in inches
        Returns:
        String: SVG sequence describing the primer over a sequence
        """

        if p_desc[3] == "+":
            body_start = p_desc[1]
            arr_len = p_desc[2] - p_desc[1] + 1
            body_len = arr_len * 0.5
            body_end = body_start + body_len - 1
            head_end = p_desc[2]
            mid_arrow = arrow_height/2

        else:
            body_start = p_desc[2]
            arr_len = p_desc[2] - p_desc[1] + 1
            body_len = arr_len * 0.5
            body_end = body_start - body_len + 1
            head_end = p_desc[1]
            mid_arrow = arrow_height/2

        path = 'M '+str(body_start)+',0 L'+str(body_end) +\
               ',0 L'+str(head_end)+','+str(mid_arrow) +\
               ' L'+str(body_end)+','+str(arrow_height) +\
               ' L'+str(body_start)+','+str(arrow_height)+' Z'

        return path

    def generate_primers_report(self):
        """Generates a HTML report with the primers statistics
        """
        env = Environment(loader=FileSystemLoader(self.report_template_folder))
        template = env.get_template("primers.html")

        primers = dict()
        f_scores = dict()

        # retrieve all primers in the selected pairs
        for pair in self.ppairs:
            primers[pair.a.id] = pair.a
            primers[pair.b.id] = pair.b
            f_scores[pair.a.id] = pair.a_fscore
            f_scores[pair.b.id] = pair.b_fscore

        primers_info = []
        primers_res = []
        output_name = self.args.output_prefix

        tmp_res = [["Total number of primers generated:",
                    str(self.n_raw_probes)],
                   ["Primers filtered by N bases:",
                    str(self.pb_filtered["n"])],
                   ["Primers filtered by melting temperature:",
                    str(self.pb_filtered["mt"])],
                   ["Primers filtered by GC content:",
                    str(self.pb_filtered["gc"])],
                   ["Primers filtered by LCC:",
                    str(self.pb_filtered["lcc"])],
                   ["Primers filtered by homodimer formation:",
                    str(self.pb_filtered["ghm"])],
                   ["Primers filtered by hairpin formation:",
                    str(self.pb_filtered["gss"])],
                   ["Total primer kept after filtering:",
                    str(self.pb_filtered["keep"])],
                   ["Total primers reported:",
                    str(len(primers))]]

        for row in tmp_res:
            primers_res.append(dict(parameter=row[0], value=row[1]))

        flag = 0
        for primer in primers:

            if flag == 0:
                display = "block"
                flag += 1
            else:
                display = "none"

            primer_ob = primers[primer]

            tgts_ids = [record.id for record in self.targets_records]
            seqs_dtd = [seq_id for seq_id in primer_ob.alignments]
            tgt_detected = len([elm for elm in seqs_dtd if elm in tgts_ids])

            tmp = [["Sequence:", str(primer_ob.seq)],
                   ["Melting temperature:", str(primer_ob.mt)+" C"],
                   ["GC percentage:", str(primer_ob.gc)+"%"],
                   ["Local composition complexity:", str(primer_ob.lcc)],
                   ["Energy for homodimer formation:",
                    str(primer_ob.dghm) + " kcal/mol"],
                   ["Energy for hairpin formation:",
                    str(primer_ob.dgss)+" kcal/mol"],
                   ["SDSS start:", str(primer_ob.sdss_start)],
                   ["Total number of sequences detected:",
                    str(len(primer_ob.alignments))],
                   ["Number of targets detected:", str(tgt_detected)],
                   ["FScore:", str(f_scores[primer])]]

            info = []
            for i in range(len(tmp)):
                row = i + 1
                if (row % 2) == 0:
                    row_class = "even"
                else:
                    row_class = "odd"

                info.append(dict(row_class=row_class,
                                 parameter=tmp[i][0],
                                 value=tmp[i][1]))

            primers_info.append(dict(id=primer_ob.id,
                                     info=info,
                                     display=display))

        final_info = dict(output_name=output_name,
                          primers_res=primers_res,
                          primers_info=primers_info)

        html_output = template.render(final_info)

        return html_output
