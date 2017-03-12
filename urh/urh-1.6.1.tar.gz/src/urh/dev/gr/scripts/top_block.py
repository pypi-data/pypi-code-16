#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Top Block
# Generated: Sun Mar 12 14:50:39 2017
##################################################

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print "Warning: failed to XInitThreads()"

from gnuradio import eng_notation
from gnuradio import gr
from gnuradio import wxgui
from gnuradio.eng_option import eng_option
from gnuradio.fft import window
from gnuradio.filter import firdes
from gnuradio.wxgui import fftsink2
from gnuradio.wxgui import forms
from grc_gnuradio import wxgui as grc_wxgui
from optparse import OptionParser
import osmosdr
import wx


class top_block(grc_wxgui.top_block_gui):

    def __init__(self):
        grc_wxgui.top_block_gui.__init__(self, title="Top Block")

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 1000000
        self.gain_slider = gain_slider = 50
        self.gain = gain = 30
        self.freq = freq = 433000
        self.bw = bw = 200000
        self.bb_gain_slider = bb_gain_slider = 50

        ##################################################
        # Blocks
        ##################################################
        _gain_slider_sizer = wx.BoxSizer(wx.VERTICAL)
        self._gain_slider_text_box = forms.text_box(
        	parent=self.GetWin(),
        	sizer=_gain_slider_sizer,
        	value=self.gain_slider,
        	callback=self.set_gain_slider,
        	label='gain_slider',
        	converter=forms.float_converter(),
        	proportion=0,
        )
        self._gain_slider_slider = forms.slider(
        	parent=self.GetWin(),
        	sizer=_gain_slider_sizer,
        	value=self.gain_slider,
        	callback=self.set_gain_slider,
        	minimum=0,
        	maximum=100,
        	num_steps=100,
        	style=wx.SL_HORIZONTAL,
        	cast=float,
        	proportion=1,
        )
        self.Add(_gain_slider_sizer)
        _bb_gain_slider_sizer = wx.BoxSizer(wx.VERTICAL)
        self._bb_gain_slider_text_box = forms.text_box(
        	parent=self.GetWin(),
        	sizer=_bb_gain_slider_sizer,
        	value=self.bb_gain_slider,
        	callback=self.set_bb_gain_slider,
        	label='bb_gain_slider',
        	converter=forms.float_converter(),
        	proportion=0,
        )
        self._bb_gain_slider_slider = forms.slider(
        	parent=self.GetWin(),
        	sizer=_bb_gain_slider_sizer,
        	value=self.bb_gain_slider,
        	callback=self.set_bb_gain_slider,
        	minimum=0,
        	maximum=100,
        	num_steps=100,
        	style=wx.SL_HORIZONTAL,
        	cast=float,
        	proportion=1,
        )
        self.Add(_bb_gain_slider_sizer)
        self.wxgui_fftsink2_0 = fftsink2.fft_sink_c(
        	self.GetWin(),
        	baseband_freq=0,
        	y_per_div=10,
        	y_divs=10,
        	ref_level=0,
        	ref_scale=2.0,
        	sample_rate=samp_rate,
        	fft_size=1024,
        	fft_rate=15,
        	average=False,
        	avg_alpha=None,
        	title='FFT Plot',
        	peak_hold=False,
        )
        self.Add(self.wxgui_fftsink2_0.win)
        self.osmosdr_source_0 = osmosdr.source( args="numchan=" + str(1) + " " + '' )
        self.osmosdr_source_0.set_sample_rate(samp_rate)
        self.osmosdr_source_0.set_center_freq(freq, 0)
        self.osmosdr_source_0.set_freq_corr(0, 0)
        self.osmosdr_source_0.set_dc_offset_mode(0, 0)
        self.osmosdr_source_0.set_iq_balance_mode(0, 0)
        self.osmosdr_source_0.set_gain_mode(False, 0)
        self.osmosdr_source_0.set_gain(14, 0)
        self.osmosdr_source_0.set_if_gain(gain_slider, 0)
        self.osmosdr_source_0.set_bb_gain(bb_gain_slider, 0)
        self.osmosdr_source_0.set_antenna('', 0)
        self.osmosdr_source_0.set_bandwidth(bw, 0)
          

        ##################################################
        # Connections
        ##################################################
        self.connect((self.osmosdr_source_0, 0), (self.wxgui_fftsink2_0, 0))    

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.wxgui_fftsink2_0.set_sample_rate(self.samp_rate)
        self.osmosdr_source_0.set_sample_rate(self.samp_rate)

    def get_gain_slider(self):
        return self.gain_slider

    def set_gain_slider(self, gain_slider):
        self.gain_slider = gain_slider
        self._gain_slider_slider.set_value(self.gain_slider)
        self._gain_slider_text_box.set_value(self.gain_slider)
        self.osmosdr_source_0.set_if_gain(self.gain_slider, 0)

    def get_gain(self):
        return self.gain

    def set_gain(self, gain):
        self.gain = gain

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.osmosdr_source_0.set_center_freq(self.freq, 0)

    def get_bw(self):
        return self.bw

    def set_bw(self, bw):
        self.bw = bw
        self.osmosdr_source_0.set_bandwidth(self.bw, 0)

    def get_bb_gain_slider(self):
        return self.bb_gain_slider

    def set_bb_gain_slider(self, bb_gain_slider):
        self.bb_gain_slider = bb_gain_slider
        self._bb_gain_slider_slider.set_value(self.bb_gain_slider)
        self._bb_gain_slider_text_box.set_value(self.bb_gain_slider)
        self.osmosdr_source_0.set_bb_gain(self.bb_gain_slider, 0)


def main(top_block_cls=top_block, options=None):

    tb = top_block_cls()
    tb.Start(True)
    tb.Wait()


if __name__ == '__main__':
    main()
