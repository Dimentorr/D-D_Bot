
class PersonData:
    def __init__(self, name_user, password):
        self.user_id = int
        self.name_user = name_user
        self.password = password
        self.id_characters = []
        self.now_location = 'start'
        self.last_location = 'start'
        self.premium = False


class PlayerSheet:
    def __init__(self):
        self.data_unit = \
            {
                'BaseInformation':
                    {
                        'InvisibleID': '',
                        'NamePlayer': '',
                        'NameUnit': '',
                        'Class': '',
                        'Story': '',
                        'Worldview': '',
                        'XP': 0,
                        'Level': 1
                    },
                'SavingThrows':
                    {
                        'Success': 0,
                        'Failure': 0
                    },
                'Attributes':
                    {
                        'Strong': 0,
                        'Sleight': 0,
                        'Body': 0,
                        'Intelligence': 0,
                        'Wisdom': 0,
                        'Charisma': 0
                    },
                'DiceForHP':
                    {
                        'Count': 1,
                        'Dice': 0
                    },
                'PersonalTraits':
                    {
                        'CharacterTraits': [],
                        'Ideals': [],
                        'Attachments': [],
                        'Weaknesses': []
                    },
                'Possessions/abilities':
                    {
                        'Possessions': [],
                        'abilities': []
                    },
                'BattleStats':
                    {
                        'Defence': 0,
                        'Initiative': 0,
                        'Speed': 0,
                        'MaxHP': 0,
                        'NowHP': 0
                    },
                'Skills':
                    {
                        'Selected': []
                    },
                'SavingThrowsAttributes':
                    {
                        'Selected': []
                    },
                'Inventory':
                    {
                        'Cash':
                            {
                                'Platinum': 0,
                                'Gold': 0,
                                'Silver': 0,
                                'Copper': 0
                            },
                        'Bag': []
                    },
                'Magic':
                    {
                        'Base':
                            {
                                'Class': '',
                                'Attribute': '',
                                'DifficultSavingThrows': 0,
                                'BonusAttack': 0
                            },
                        'MagicalCircle':
                            {
                                '0':
                                    {
                                        'CountAll': 0,
                                        'BattleCount': 0,
                                        'Spells': []
                                    },
                                '1':
                                    {
                                        'CountAll': 0,
                                        'BattleCount': 0,
                                        'Spells': []
                                    },
                                '2':
                                    {
                                        'CountAll': 0,
                                        'BattleCount': 0,
                                        'Spells': []
                                    },
                                '3':
                                    {
                                        'CountAll': 0,
                                        'BattleCount': 0,
                                        'Spells': []
                                    },
                                '4':
                                    {
                                        'CountAll': 0,
                                        'BattleCount': 0,
                                        'Spells': []
                                    },
                                '5':
                                    {
                                        'CountAll': 0,
                                        'BattleCount': 0,
                                        'Spells': []
                                    },
                                '6':
                                    {
                                        'CountAll': 0,
                                        'BattleCount': 0,
                                        'Spells': []
                                    },
                                '7':
                                    {
                                        'CountAll': 0,
                                        'BattleCount': 0,
                                        'Spells': []
                                    },
                                '8':
                                    {
                                        'CountAll': 0,
                                        'BattleCount': 0,
                                        'Spells': []
                                    },
                                '9':
                                    {
                                        'CountAll': 0,
                                        'BattleCount': 0,
                                        'Spells': []
                                    }
                            }
                    }
            }

