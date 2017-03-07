if not 'Agent' in fsschema:
    drop_entity_type('Agent')

drop_relation_type('associated_for')
