from collective.geo.mapwidget.maplayers import MapLayer
from collective.geo.zugmap import _


class ZugMapOrtsplanLayer(MapLayer):
    name = u"zugmap_ortsplan"
    Title = _(u"Zugmap Ortsplan (GIS Kanton Zug)")
    type = 'zugmap'


class ZugMapOrthofotoPlus(MapLayer):
    name = u"zugmap_orthofotoplus"
    Title = _(u"Zugmap LuftbildPlus+ (GIS Kanton Zug)")
    type = 'zugmap'
