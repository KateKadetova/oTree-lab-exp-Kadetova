from otree.api import *
import random


doc = """
Randomized vignette experiment about AI-mediated interpersonal communication.
Participants read the same supportive message under one of three randomly assigned
conditions: written by a human, written by a human with AI assistance, or generated
by AI and sent almost without changes.
"""


class C(BaseConstants):
    NAME_IN_URL = 'ai_communication'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    CONDITIONS = ['human', 'ai_assisted', 'ai_generated']

    LIKERT_CHOICES = [
        [1, '1 — Полностью не согласен(на)'],
        [2, '2 — Скорее не согласен(на)'],
        [3, '3 — Немного не согласен(на)'],
        [4, '4 — Ни согласен(на), ни не согласен(на)'],
        [5, '5 — Немного согласен(на)'],
        [6, '6 — Скорее согласен(на)'],
        [7, '7 — Полностью согласен(на)'],
    ]


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    condition = models.StringField()

    # Готовность к взаимности
    reciprocity_support = models.IntegerField(
        label='Я был(а) бы готов(а) поддержать этого друга в похожей ситуации',
        choices=C.LIKERT_CHOICES,
        widget=widgets.RadioSelect,
    )
    reciprocity_time = models.IntegerField(
        label='Я был(а) бы готов(а) потратить свое время, чтобы помочь этому другу',
        choices=C.LIKERT_CHOICES,
        widget=widgets.RadioSelect,
    )
    reciprocity_future_help = models.IntegerField(
        label='Если бы этот друг оказался в сложной ситуации, я бы захотел(а) ему помочь',
        choices=C.LIKERT_CHOICES,
        widget=widgets.RadioSelect,
    )

    # Воспринимаемые усилия
    effort_significant = models.IntegerField(
        label='Друг вложил значительные усилия в создание этого сообщения',
        choices=C.LIKERT_CHOICES,
        widget=widgets.RadioSelect,
    )
    effort_words = models.IntegerField(
        label='Друг внимательно подбирал слова, чтобы меня поддержать',
        choices=C.LIKERT_CHOICES,
        widget=widgets.RadioSelect,
    )
    effort_time = models.IntegerField(
        label='Друг потратил время на то, чтобы написать это сообщение',
        choices=C.LIKERT_CHOICES,
        widget=widgets.RadioSelect,
    )

    # Воспринимаемая аутентичность
    authenticity_sincere = models.IntegerField(
        label='Сообщение кажется мне искренним',
        choices=C.LIKERT_CHOICES,
        widget=widgets.RadioSelect,
    )
    authenticity_personal = models.IntegerField(
        label='Сообщение кажется мне личным, а не шаблонным',
        choices=C.LIKERT_CHOICES,
        widget=widgets.RadioSelect,
    )
    authenticity_real_feelings = models.IntegerField(
        label='Сообщение отражает настоящие чувства отправителя',
        choices=C.LIKERT_CHOICES,
        widget=widgets.RadioSelect,
    )

    # Проверка понимания условия
    manipulation_check = models.StringField(
        label='Согласно описанию, как было создано сообщение?',
        choices=[
            ['human', 'Друг написал сообщение самостоятельно, без ИИ'],
            ['ai_assisted', 'Друг использовал ИИ для помощи с формулировками и редактированием'],
            ['ai_generated', 'Друг попросил ИИ сгенерировать сообщение и отправил его почти без изменений'],
            ['unsure', 'Затрудняюсь ответить'],
        ],
        widget=widgets.RadioSelect,
    )

    # Отношение к ИИ и проверка внимательности
    ai_acceptable = models.IntegerField(
        label='Использование ИИ для личных сообщений кажется мне приемлемым',
        choices=C.LIKERT_CHOICES,
        widget=widgets.RadioSelect,
    )
    ai_self_use = models.IntegerField(
        label='Я сам(а) мог(ла) бы использовать ИИ для написания сообщения поддержки',
        choices=C.LIKERT_CHOICES,
        widget=widgets.RadioSelect,
    )
    ai_frequency = models.IntegerField(
        label='Я часто использую ИИ для помощи с текстами',
        choices=C.LIKERT_CHOICES,
        widget=widgets.RadioSelect,
    )
    attention_check = models.IntegerField(
        label='Чтобы подтвердить, что вы внимательно читаете вопрос, выберите вариант «6 — Скорее согласен(на)»',
        choices=C.LIKERT_CHOICES,
        widget=widgets.RadioSelect,
    )

    # Демография
    age = models.IntegerField(
        label='Ваш возраст',
        min=13,
        max=100,
    )
    gender = models.StringField(
        label='Ваш пол',
        choices=[
            ['female', 'Женский'],
            ['male', 'Мужской'],
            ['other', 'Другое / предпочитаю не отвечать'],
        ],
        widget=widgets.RadioSelect,
    )
    education_level = models.StringField(
        label='Ваш уровень обучения',
        choices=[
            ['bachelor', 'Бакалавриат'],
            ['master', 'Магистратура'],
            ['phd', 'Аспирантура'],
            ['other', 'Другое'],
        ],
        widget=widgets.RadioSelect,
    )

    passed_manipulation_check = models.BooleanField(initial=False)
    passed_attention_check = models.BooleanField(initial=False)


# FUNCTIONS

def creating_session(subsession: Subsession):
    players = subsession.get_players()
    random.shuffle(players)

    for i, player in enumerate(players):
        player.condition = C.CONDITIONS[i % len(C.CONDITIONS)]


def condition_text(player: Player):
    if player.condition == 'human':
        return 'Ваш друг написал это сообщение самостоятельно, без использования искусственного интеллекта.'
    if player.condition == 'ai_assisted':
        return 'Ваш друг сам сформулировал основную мысль сообщения, но использовал искусственный интеллект, чтобы подобрать формулировки и улучшить текст.'
    return 'Ваш друг попросил искусственный интеллект сгенерировать сообщение поддержки и отправил полученный текст почти без изменений.'


def condition_label(player: Player):
    if player.condition == 'human':
        return 'Сообщение написано человеком самостоятельно'
    if player.condition == 'ai_assisted':
        return 'Сообщение написано человеком с помощью ИИ'
    return 'Сообщение сгенерировано ИИ почти без изменений'


# PAGES

class Consent(Page):
    pass


class Vignette(Page):
    @staticmethod
    def vars_for_template(player: Player):
        scenario_text = """
        Представьте, что вы плохо написали важный экзамен по предмету, который был для вас значим.
        Вы готовились к нему заранее, рассчитывали на хороший результат, но после экзамена поняли,
        что справились хуже, чем ожидали. Из-за этого вы расстроены, сомневаетесь в своих способностях
        и переживаете, что эта неудача может повлиять на вашу дальнейшую учёбу.
        После этого ваш близкий друг присылает вам сообщение со словами поддержки.
        """

        support_message = """
        Слушай, мне очень жаль, что экзамен прошёл не так, как ты ожидал. Я понимаю, что тебе сейчас
        обидно и тревожно, особенно потому что ты правда готовился и рассчитывал на другой результат.
        Но один неудачный экзамен не говорит о том, что ты не справишься дальше или что твои усилия
        были напрасны.

        Мне кажется, сейчас важно немного выдохнуть и не делать выводы о себе только по одному дню.
        Ты уже много раз показывал, что умеешь разбираться в сложных вещах и доводить дела до конца.
        Когда немного успокоишься, можно будет спокойно посмотреть, что именно пошло не так, и понять,
        как это исправить. Я рядом, и, если захочешь обсудить это или просто отвлечься, напиши мне.
        """

        return dict(
            condition_label=condition_label(player),
            condition_text=condition_text(player),
            scenario_text=scenario_text,
            support_message=support_message,
        )


class EffortQuestions(Page):
    form_model = 'player'
    form_fields = ['effort_significant', 'effort_words', 'effort_time']


class AuthenticityQuestions(Page):
    form_model = 'player'
    form_fields = ['authenticity_sincere', 'authenticity_personal', 'authenticity_real_feelings']


class ReciprocityQuestions(Page):
    form_model = 'player'
    form_fields = ['reciprocity_support', 'reciprocity_time', 'reciprocity_future_help']


class ManipulationCheck(Page):
    form_model = 'player'
    form_fields = ['manipulation_check']

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.passed_manipulation_check = player.manipulation_check == player.condition


class AIAttitudes(Page):
    form_model = 'player'
    form_fields = ['ai_acceptable', 'ai_self_use', 'ai_frequency', 'attention_check']

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.passed_attention_check = player.attention_check == 6


class Demographics(Page):
    form_model = 'player'
    form_fields = ['age', 'gender', 'education_level']


class Debrief(Page):
    pass


page_sequence = [
    Consent,
    Vignette,
    EffortQuestions,
    AuthenticityQuestions,
    ReciprocityQuestions,
    ManipulationCheck,
    AIAttitudes,
    Demographics,
    Debrief,
]
