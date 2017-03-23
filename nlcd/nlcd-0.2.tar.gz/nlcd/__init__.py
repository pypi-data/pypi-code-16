years = [1992, 2001, 2006, 2011]

values = {'11': 'Open Water',
          '12': 'Perennial Ice/Snow',
          '21': 'Developed, Open Space',
          '22': 'Developed, Low Intensity',
          '23': 'Developed, Medium Intensity',
          '24': 'Developed High Intensity',
          '31': 'Barren Land (Rock/Sand/Clay)',
          '41': 'Deciduous Forest',
          '42': 'Evergreen Forest',
          '43': 'Mixed Forest',
          '51': 'Dwarf Scrub',
          '52': 'Shrub/Scrub',
          '71': 'Grassland/Herbaceous',
          '72': 'Sedge/Herbaceous',
          '73': 'Lichens',
          '74': 'Moss',
          '81': 'Pasture/Hay',
          '82': 'Cultivated Crops',
          '90': 'Woody Wetlands',
          '95': 'Emergent Herbaceous Wetlands'
          }

categories = {'Water': ('11', '12'),
              'Developed': ('21', '22', '23', '24'),
              'Barren': ('31',),
              'Forest': ('41', '42', '43'),
              'Shrubland': ('51', '52'),
              'Herbaceous': ('71', '72', '73', '74'),
              'Planted': ('81', '82'),
              'Wetlands': ('90', '95')
              }

categories_1992_change = {'Water': ('1', '12', '13', '14', '15',
                                    '16', '17', '18'),
                          'Developed': ('2', '21', '23', '24', '25',
                                        '26', '27', '28'),
                          'Barren': ('3', '31', '32', '34', '35',
                                     '36', '37', '38'),
                          'Forest': ('4', '41', '42', '43', '45',
                                     '46', '47', '48'),
                          'Shrubland': ('5', '51', '52', '53', '54',
                                        '56', '57', '58'),
                          'Planted': ('6', '61', '62', '63', '64',
                                      '65', '67', '68'),
                          'Wetlands': ('7', '71', '72', '73', '74',
                                       '75', '76'),
                          }

