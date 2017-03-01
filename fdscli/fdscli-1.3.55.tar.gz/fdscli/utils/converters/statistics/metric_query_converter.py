from fdscli.model.statistics.context_def import ContextDef
import json
from fdscli.utils.converters.statistics.date_range_converter import DateRangeConverter

class MetricQueryConverter(object):
    '''
    Created on Jun 29, 2015
    
    @author: nate
    '''

    @staticmethod
    def to_json(query):
        
#         if not isinstance(query, MetricQueryCriteria):
#             raise TypeError("Must be a metric query criteria.")
#         
        q_json = dict()
        
        context_array = []
        
        for context in query.contexts:
            if isinstance(context, ContextDef):
                c_dict = dict()
                c_dict["contextType"] = context.context_type
                c_dict["contextId"] = context.context_id
                context_array.append( c_dict )
        
        q_json["contexts"] = context_array
        q_json["range"] = json.loads( DateRangeConverter.to_json(query.date_range) )
        
        metrics = []
        
        for metric in query.metrics:
            metrics.append( metric[0] )
            
        q_json["seriesType"] = metrics
        
        if query.points is not None:
            q_json["points"] = query.points
        
        q_json = json.dumps(q_json)
        
        return q_json
