from Acquisition import aq_inner
from Acquisition import aq_parent
from plone import api
from esdrt.content.reviewfolder import IReviewFolder

def grant_local_roles(context):
    """ add local roles to the groups when adding an observation
    """
    country = context.country.lower()
    sector = context.ghg_source_category_value()
    applyes_to = [context]
    parent = aq_parent(aq_inner(context))
    if IReviewFolder.providedBy(parent):
        applyes_to.append(parent)
    
    context.__ac_local_roles_block__ = True
            
    for obj in applyes_to:
        api.group.grant_roles(
            groupname='extranet-esd-ghginv-sr-%s-%s' % (sector, country),
            roles=['ReviewerPhase1'],
            obj=obj,
        )
        api.group.grant_roles(
            groupname='extranet-esd-ghginv-qualityexpert-%s' % sector,
            roles=['QualityExpert'],
            obj=obj,
        )
        api.group.grant_roles(
            groupname='extranet-esd-esdreview-reviewexp-%s-%s' % (sector, country),
            roles=['ReviewerPhase2'],
            obj=obj,
        )
        api.group.grant_roles(
            groupname='extranet-esd-esdreview-leadreview-%s' % country,
            roles=['LeadReviewer'],
            obj=obj,
        )
        api.group.grant_roles(
            groupname='extranet-esd-countries-msa-%s' % country,
            roles=['MSAuthority'],
            obj=obj,
        )
