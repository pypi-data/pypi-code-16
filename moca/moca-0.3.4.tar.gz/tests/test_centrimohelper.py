"""
Tests for fasta helper
"""
import unittest
from moca.helpers import centrimo

class TestCentrimoHelper(unittest.TestCase):
    """Test centrimo helper"""
    def setUp(self):
        self.centrimo_txt = 'tests/data/ENCSR000AKB/moca_output/centrimo_out/centrimo.txt'
        self.centrimo_stats = 'tests/data/ENCSR000AKB/moca_output/centrimo_out/site_counts.txt'

    def test_txtreader(self):
        centrimo_dict = centrimo.read_centrimo_txt(self.centrimo_txt)
        """
        # db	id                         alt	 E-value	adj_p-value	log_adj_p-value	bin_location	bin_width	total_width	sites_in_bin	total_sites	p_success	 p-value	mult_tests
        1	1                         MEME	1.1e-220	   3.8e-221	        -507.55	         0.0	       39	        187	         431	        490	  0.20856	4.0e-223	        93
        1	2                         MEME	3.0e0000	   1.0e0000	           0.00	         0.0	        1	        181	           0	        223	  0.00552	1.0e0000	        90
        1	3                         MEME	3.0e0000	   1.0e0000	           0.00	         0.0	        1	        187	           1	        298	  0.00535	8.0e-001	        93
        """
        assert centrimo_dict[0]['adj_p-value'] == '3.8e-221'
        assert centrimo_dict[1]['adj_p-value'] == '1.0e0000'
        assert centrimo_dict[2]['adj_p-value'] == '1.0e0000'
        assert centrimo_dict[0]['E-value'] == '1.1e-220'
        assert centrimo_dict[1]['E-value'] == '3.0e0000'
        assert centrimo_dict[2]['E-value'] == '3.0e0000'

    def test_stats(self):
        all_stats = centrimo.read_centrimo_stats(self.centrimo_stats)
        motif_stats = all_stats['MEME']['MOTIF_{}'.format(1)]
        X_values = motif_stats['pos']
        Y_values = motif_stats['count']
        X_expected = [-93.0, -92.0, -91.0, -90.0, -89.0, -88.0, -87.0, -86.0, -85.0,
                      -84.0, -83.0, -82.0, -81.0, -80.0, -79.0, -78.0, -77.0, -76.0,
                      -75.0, -74.0, -73.0, -72.0, -71.0, -70.0, -69.0, -68.0, -67.0,
                      -66.0, -65.0, -64.0, -63.0, -62.0, -61.0, -60.0, -59.0, -58.0,
                      -57.0, -56.0, -55.0, -54.0, -53.0, -52.0, -51.0, -50.0, -49.0,
                      -48.0, -47.0, -46.0, -45.0, -44.0, -43.0, -42.0, -41.0, -40.0,
                      -39.0, -38.0, -37.0, -36.0, -35.0, -34.0, -33.0, -32.0, -31.0,
                      -30.0, -29.0, -28.0, -27.0, -26.0, -25.0, -24.0, -23.0, -22.0,
                      -21.0, -20.0, -19.0, -18.0, -17.0, -16.0, -15.0, -14.0, -13.0,
                      -12.0, -11.0, -10.0, -9.0, -8.0, -7.0, -6.0, -5.0, -4.0, -3.0,
                      -2.0, -1.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0,
                      11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0, 21.0,
                      22.0, 23.0, 24.0, 25.0, 26.0, 27.0, 28.0, 29.0, 30.0, 31.0, 32.0,
                      33.0, 34.0, 35.0, 36.0, 37.0, 38.0, 39.0, 40.0, 41.0, 42.0, 43.0,
                      44.0, 45.0, 46.0, 47.0, 48.0, 49.0, 50.0, 51.0, 52.0, 53.0, 54.0,
                      55.0, 56.0, 57.0, 58.0, 59.0, 60.0, 61.0, 62.0, 63.0, 64.0, 65.0,
                      66.0, 67.0, 68.0, 69.0, 70.0, 71.0, 72.0, 73.0, 74.0, 75.0, 76.0,
                      77.0, 78.0, 79.0, 80.0, 81.0, 82.0, 83.0, 84.0, 85.0, 86.0, 87.0,
                      88.0, 89.0, 90.0, 91.0, 92.0, 93.0]
        Y_expected = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                      0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                      0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0,
                      0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 2.0,
                      1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 3.0, 2.0, 2.0,
                      1.0, 0.0, 1.0, 0.0, 1.0, 1.0, 3.0, 4.0, 2.0, 2.0, 2.0, 6.0, 7.0,
                      6.0, 7.0, 5.0, 6.0, 15.0, 13.0, 18.0, 17.0, 10.0, 15.0, 13.0, 16.0,
                      24.0, 18.0, 21.0, 19.0, 18.0, 19.0, 18.0, 15.0, 14.0, 7.0, 12.0, 11.0,
                      13.0, 14.0, 8.0, 3.0, 6.0, 5.0, 5.0, 5.0, 4.0, 6.0, 8.0, 2.0, 3.0,
                      1.0, 1.0, 3.0, 0.0, 2.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 1.0, 0.0,
                      0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0,
                      0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0,
                      0.0, 0.0, 0.0, 0.0, 0.0, 2.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                      0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0,
                      0.0, 0.0]
        assert X_expected == X_values
        assert Y_expected == Y_values
