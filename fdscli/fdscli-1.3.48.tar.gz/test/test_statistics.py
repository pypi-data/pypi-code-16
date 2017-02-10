import json

import mock_functions
from fdscli.utils.converters.statistics.statistics_converter import StatisticsConverter
from fdscli.model.statistics.metric_query_criteria import MetricQueryCriteria
from fdscli.model.statistics.date_range import DateRange
from fdscli.model.statistics.metrics import Metric
from fdscli.utils.converters.statistics.metric_query_converter import MetricQueryConverter
from fdscli.utils.converters.health.system_health_converter import SystemHealthConverter
from fdscli.model.health.health_state import HealthState
from fdscli.model.health.health_category import HealthCategory
from fdscli.model.statistics.context_def import ContextDef
from fdscli.model.statistics.firebreak_query_criteria import FirebreakQueryCriteria
from fdscli.utils.converters.statistics.firebreak_query_converter import FirebreakQueryConverter
from test.base_cli_test import BaseCliTest
from mock import patch

class TestStatistics(BaseCliTest):
    '''
    Created on Jun 29, 2015
    
    @author: nate
    '''

    def test_conversion(self):
        '''
        test that we can read the JSON into our objects
        '''
        
        j_str = "{\"metadata\":[],\"series\":[{\"datapoints\":[{\"x\":0,\"y\":1},{\"x\":1,\"y\":2}],\"type\":\"GETS\"},{\"datapoints\":[{\"x\":30,\"y\":100}],\"type\":\"PUTS\"}],\"calculated\":[{\"key\": \"average\", \"value\":23.23},{\"key\":\"total\", \"value\":300}]}"
        
        j_str = json.loads(j_str)

        stats = StatisticsConverter.build_statistics_from_json(j_str)
        
        assert len(stats.series_list) == 2
        assert len(stats.series_list[0].datapoints) == 2
        assert stats.series_list[0].datapoints[1].y == 2
        assert len(stats.calculated_values) == 2
        assert stats.calculated_values[0].key == "average"
        assert stats.calculated_values[1].key == "total"
        assert stats.calculated_values[1].value == 300
        
        # go back to json?
        new_str = StatisticsConverter.to_json(stats)
        p_str = '{"series": [{"seriesType": "GETS", "datapoints": [{"y": 1, "x": 0}, {"y": 2, "x": 1}]}, {"seriesType": "PUTS", "datapoints": [{"y": 100, "x": 30}]}], "calculated": [{"value": 23.23, "key": "average"}, {"value": 300, "key": "total"}], "metadata": []}'
        
        assert p_str == new_str, "Expected \n{}\nto be\n{}".format(p_str, new_str)
        
    def test_query_conversion_to_json(self):
        
        m_query = MetricQueryCriteria()
        
        m_query.contexts = [ContextDef( ContextDef.VOLUME, 7)]
        m_query.date_range = DateRange(start=1000, end=3000)
        m_query.metrics = [Metric.GETS, Metric.PUTS, Metric.SSD_GETS]
        
        j_str = MetricQueryConverter.to_json( m_query )
        real_str = '{"contexts": [{"contextType": "VOLUME", "contextId": 7}], "range": {"start": 1000, "end": 3000}, "seriesType": ["GETS", "PUTS", "SSD_GETS"]}'
        
        assert j_str == real_str, "Expected {} but got \n{}".format( real_str, j_str )
        
    def test_fb_query_conversion_to_json(self):
        
        m_query = FirebreakQueryCriteria()
        
        m_query.contexts = [ContextDef( ContextDef.VOLUME, 8)]
        m_query.date_range = DateRange(start=1000, end=3000)
        m_query.use_size_for_value = True
        m_query.points = 1
        
        j_str = FirebreakQueryConverter.to_json( m_query )
        real_str = '{"contexts": [{"contextType": "VOLUME", "contextId": 8}], "range": {"start": 1000, "end": 3000}, "mostRecentResults": 1, "seriesType": ["STC_SIGMA", "LTC_SIGMA", "STP_SIGMA", "LTP_SIGMA"], "useSizeForValue": true}'

        assert j_str == real_str, "Expected {} but got \n{}".format( real_str, j_str )
        
    def test_system_health_conversion(self):
        
        j_str = '{"overall":"ACCEPTABLE","status":[{"state":"GOOD","category":"CAPACITY","message":"l_capacity_good"},{"state":"BAD","category":"SERVICES","message":"l_services_bad"}]}'
        
        sys_health = SystemHealthConverter.build_system_health_from_json(j_str)
        
        assert len(sys_health.health_records) == 2
        assert sys_health.overall_health == HealthState.ACCETPABLE
        assert sys_health.health_records[0].category == HealthCategory.CAPACITY
        assert sys_health.health_records[1].category == HealthCategory.SERVICES
        assert sys_health.health_records[0].state == HealthState.GOOD
        assert sys_health.health_records[1].state == HealthState.BAD
        
    @patch( "fdscli.services.volume_service.VolumeService.get_volume", side_effect=mock_functions.findVolumeById)
    @patch( "fdscli.services.stats_service.StatsService.query_volume_metrics", side_effect=mock_functions.fakeStats)
    def test_vol_stat_query(self, query, get_vol):
        
        args = ["stats", "volumes", "-metrics", "GETS", "-volume_ids", "1"]
        
        self.callMessageFormatter(args)
        self.cli.run(args)
        
        # no longer need to make this call
        assert get_vol.call_count == 0
        
        metric_query = query.call_args[0][0]
        
        assert isinstance(metric_query, MetricQueryCriteria)
        assert len(metric_query.contexts) == 1
        assert metric_query.contexts[0].context_id == 1
        assert len( metric_query.metrics ) == 1
        assert metric_query.metrics[0] == Metric.GETS
        assert query.call_count == 1
        
    @patch( "fdscli.services.volume_service.VolumeService.get_volume", side_effect=mock_functions.findVolumeById)
    @patch( "fdscli.services.stats_service.StatsService.query_firebreak_metrics", side_effect=mock_functions.fakeStats)
    def test_fb_stat_query(self, query, get_vol):
        
        args = ["stats", "firebreak", "-size_for_value=false", "-most_recent=2", "-volume_ids", "1"]
        
        self.callMessageFormatter(args)
        self.cli.run(args)
        
        assert query.call_count == 1
        # no longer need to make this call
        assert get_vol.call_count == 0
        
        fb_query = query.call_args[0][0]
        
        assert isinstance(fb_query, FirebreakQueryCriteria)
        assert len(fb_query.contexts) == 1
        assert fb_query.contexts[0].context_id == 1
        assert len( fb_query.metrics ) == 4
        assert fb_query.metrics[0] == Metric.STC_SIGMA
        assert fb_query.metrics[1] == Metric.LTC_SIGMA
        assert fb_query.metrics[2] == Metric.STP_SIGMA
        assert fb_query.metrics[3] == Metric.LTP_SIGMA
        assert fb_query.points == 2
        assert fb_query.use_size_for_value is False 
        
    @patch( "fdscli.services.volume_service.VolumeService.get_volume", side_effect=mock_functions.findVolumeById)
    @patch( "fdscli.services.stats_service.StatsService.query_volume_metrics", side_effect=mock_functions.fakeStats)
    def test_vol_stat_query_new_stats(self, query, get_vol):
        
        args = ["stats", "volumes", "-metrics", "COMPRESSION_RATIO_PUTS", "EXTERNAL_PUTS", "-volume_ids", "1"]
        
        self.callMessageFormatter(args)
        self.cli.run(args)
        
        # no longer need to make this call
        assert get_vol.call_count == 0
        
        metric_query = query.call_args[0][0]
        
        assert isinstance(metric_query, MetricQueryCriteria)
        assert len(metric_query.contexts) == 1
        assert metric_query.contexts[0].context_id == 1
        assert len( metric_query.metrics ) == 2
        assert metric_query.metrics[0] == Metric.COMPRESSION_RATIO_PUTS
        assert metric_query.metrics[1] == Metric.EXTERNAL_PUTS
        assert query.call_count == 1
