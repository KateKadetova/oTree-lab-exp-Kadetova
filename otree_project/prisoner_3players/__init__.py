from otree.api import *
import random


doc = """
Three-player Prisoner's Dilemma with an observer.
Players 1 and 2 choose whether to cooperate or defect.
Player 3 is an examinator and can reduce their payoffs.
The game has a random treatment assignment, several rounds,
and final payoff is based on a randomly selected round.
"""


class C(BaseConstants):
    NAME_IN_URL = 'prisoner_three'
    PLAYERS_PER_GROUP = 3
    NUM_ROUNDS = 3

    PAYOFF_A = cu(300)  # 1 предает, 1 кооперируется
    PAYOFF_B = cu(200)  # оба кооперируются
    PAYOFF_C = cu(100)  # оба предают
    PAYOFF_D = cu(0)    # 1 кооперируется, 1 предает

    OBSERVER_ENDOWMENT = cu(100)
    MAX_PUNISHMENT = cu(30)
    PUNISHMENT_MULTIPLIER = 2


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    treatment = models.StringField()

    punish_p1 = models.CurrencyField(
        min=cu(0),
        max=C.MAX_PUNISHMENT,
        label='How many punishment points do you want to assign to Player 1?',
    )

    punish_p2 = models.CurrencyField(
        min=cu(0),
        max=C.MAX_PUNISHMENT,
        label='How many punishment points do you want to assign to Player 2?',
    )


class Player(BasePlayer):
    cooperate = models.BooleanField(
        choices=[[True, 'Cooperate'], [False, 'Defect']],
        doc="""This player's decision""",
        widget=widgets.RadioSelect,
    )

    base_payoff = models.CurrencyField(initial=0)
    round_payoff = models.CurrencyField(initial=0)


# FUNCTIONS

def creating_session(subsession: Subsession):
    for group in subsession.get_groups():
        if subsession.round_number == 1:
            group.treatment = random.choice(['control', 'treatment'])

            selected_round = random.randint(1, C.NUM_ROUNDS)
            for player in group.get_players():
                player.participant.vars['selected_round'] = selected_round
        else:
            group.treatment = group.in_round(1).treatment


def get_role(player: Player):
    if player.id_in_group == 1:
        return 'Player 1'
    if player.id_in_group == 2:
        return 'Player 2'
    return 'Player 3: Observer'


def prisoner_players(group: Group):
    player1 = group.get_player_by_id(1)
    player2 = group.get_player_by_id(2)
    return player1, player2


def observer_player(group: Group):
    return group.get_player_by_id(3)


def set_payoffs(group: Group):
    player1, player2 = prisoner_players(group)
    player3 = observer_player(group)

    payoff_matrix = {
        (False, True): C.PAYOFF_A,
        (True, True): C.PAYOFF_B,
        (False, False): C.PAYOFF_C,
        (True, False): C.PAYOFF_D,
    }

    player1.base_payoff = payoff_matrix[(player1.cooperate, player2.cooperate)]
    player2.base_payoff = payoff_matrix[(player2.cooperate, player1.cooperate)]

    player1.round_payoff = max(
        cu(0),
        player1.base_payoff - C.PUNISHMENT_MULTIPLIER * group.punish_p1
    )

    player2.round_payoff = max(
        cu(0),
        player2.base_payoff - C.PUNISHMENT_MULTIPLIER * group.punish_p2
    )

    player3.round_payoff = (
        C.OBSERVER_ENDOWMENT - group.punish_p1 - group.punish_p2
    )

    for player in group.get_players():
        player.payoff = cu(0)

    if group.round_number == C.NUM_ROUNDS:
        for player in group.get_players():
            selected_round = player.participant.vars['selected_round']
            selected_player = player.in_round(selected_round)
            player.payoff = selected_player.round_payoff


# PAGES

class Introduction(Page):
    @staticmethod
    def vars_for_template(player: Player):
        if player.group.treatment == 'treatment':
            treatment_text = (
                'This is the experimental group. '
                'Players 1 and 2 are informed that Player 3 will observe their decisions '
                'and can reduce their payoffs.'
            )
        else:
            treatment_text = (
                'This is the control group. '
                'Players 1 and 2 receive only the standard decision instructions.'
            )

        return dict(
            role=get_role(player),
            treatment=player.group.treatment,
            treatment_text=treatment_text,
            round_number=player.round_number,
        )


class Decision(Page):
    form_model = 'player'
    form_fields = ['cooperate']

    @staticmethod
    def is_displayed(player: Player):
        return player.id_in_group in [1, 2]

    @staticmethod
    def vars_for_template(player: Player):
        show_observer_info = player.group.treatment == 'treatment'
        return dict(
            role=get_role(player),
            show_observer_info=show_observer_info,
        )


class ResultsWaitPage(WaitPage):
    pass


class ObserverDecision(Page):
    form_model = 'group'
    form_fields = ['punish_p1', 'punish_p2']

    @staticmethod
    def is_displayed(player: Player):
        return player.id_in_group == 3

    @staticmethod
    def vars_for_template(player: Player):
        player1, player2 = prisoner_players(player.group)

        return dict(
            p1_decision=player1.field_display('cooperate'),
            p2_decision=player2.field_display('cooperate'),
            observer_endowment=C.OBSERVER_ENDOWMENT,
            max_punishment=C.MAX_PUNISHMENT,
            punishment_multiplier=C.PUNISHMENT_MULTIPLIER,
        )


class PunishmentWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        player1, player2 = prisoner_players(player.group)

        return dict(
            role=get_role(player),
            p1_decision=player1.field_display('cooperate'),
            p2_decision=player2.field_display('cooperate'),
            punish_p1=player.group.punish_p1,
            punish_p2=player.group.punish_p2,
            base_payoff=player.base_payoff,
            round_payoff=player.round_payoff,
        )


class FinalResults(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def vars_for_template(player: Player):
        selected_round = player.participant.vars['selected_round']
        selected_player = player.in_round(selected_round)

        return dict(
            selected_round=selected_round,
            selected_round_payoff=selected_player.round_payoff,
            final_payoff=player.payoff,
        )


page_sequence = [
    Introduction,
    Decision,
    ResultsWaitPage,
    ObserverDecision,
    PunishmentWaitPage,
    Results,
    FinalResults,
]