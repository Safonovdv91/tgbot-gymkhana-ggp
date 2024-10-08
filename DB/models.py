from dataclasses import dataclass, field
from datetime import datetime


class StageSubscribers:
    __athelete_classes = (
        "A",
        "B",
        "C1",
        "C2",
        "C3",
        "D1",
        "D2",
        "D3",
        "D4",
        "N",
    )

    def __init__(self, athelete_class: str, subscribers_id: set):
        self.athlete_class = athelete_class
        self.subscribers_id = subscribers_id

    @property
    def athlete_class(self):
        return self._athlete_class

    @athlete_class.setter
    def athlete_class(self, value: str):
        if not isinstance(value, str):
            raise TypeError("Bad athelete class(type), must be str")
        if value not in self.__athelete_classes:
            raise AttributeError(f"{value} Bad athelete class(attribute)")
        self._athlete_class = value

    @property
    def subscribers_id(self):
        return self._subscribers_id

    @subscribers_id.setter
    def subscribers_id(self, value: set):
        if not isinstance(value, set):
            raise TypeError("Bad subscribers_id class(type), must be set")

        self._subscribers_id = value

    def add_subscriber(self, value: int):
        if not isinstance(value, int):
            raise TypeError("Id subscriber must be int")
        self.subscribers_id.add(value)

    def removed_subscriber(self, value: int):
        if value not in self.subscribers_id:
            raise AttributeError("Haven't that subscriber")
        self.subscribers_id.remove(value)


class Subscriber:
    def __init__(self, subscriber_id: int, sub_stage: bool, sub_stage_categories: set):
        self.subscriber_id = subscriber_id
        self.sub_stage = sub_stage
        self.sub_stage_categories = sub_stage_categories

    @property
    def subscriber_id(self):
        return self._subscriber_id

    @subscriber_id.setter
    def subscriber_id(self, value):
        if (value is None) or not (isinstance(value, int)):
            raise TypeError
        if value <= 0:
            raise AttributeError("Id must be > 0")
        self._subscriber_id = value

    @property
    def sub_stage_categories(self):
        return self._sub_stage_categories

    @sub_stage_categories.setter
    def sub_stage_categories(self, value):
        try:
            value = list(value)
        except TypeError:
            raise TypeError("Transform to SET impossible")
        if (value is None) or not (isinstance(value, list)):
            raise TypeError

        self._sub_stage_categories = value


class StageSportsmanResult:
    __slots__ = (
        "_fine",
        "_result_time_seconds",
        "_sportsman_id",
        "athlete_class",
        "motorcycle",
        "result_time",
        "user_city",
        "user_country",
        "user_full_name",
        "video",
    )

    def __init__(
        self,
        sportsman_id: int | str,
        userFullName,
        motorcycle,
        userCity,
        userCountry,
        athleteClass,
        resultTimeSeconds: int,
        resultTime,
        fine: int,
        video,
    ):
        self.sportsman_id = sportsman_id
        self.user_full_name = userFullName
        self.motorcycle = motorcycle
        self.user_city = userCity
        self.user_country = userCountry
        self.athlete_class = athleteClass
        self.result_time_seconds = resultTimeSeconds
        self.result_time = resultTime
        self.fine = fine
        self.video = video

    @property
    def sportsman_id(self):
        return self._sportsman_id

    @sportsman_id.setter
    def sportsman_id(self, value: int):
        if not isinstance(value, int):
            raise TypeError("Id must be Integer")
        if value <= 0:
            raise AttributeError("ID must be positive value")

        self._sportsman_id = value

    @property
    def result_time_seconds(self):
        return self._result_time_seconds

    @result_time_seconds.setter
    def result_time_seconds(self, value: int):
        if not isinstance(value, int):
            raise TypeError("Result Time must be Integer")
        if value < 0:
            raise AttributeError("Result must be positive value")
        self._result_time_seconds = value

    @property
    def fine(self):
        return self._fine

    @fine.setter
    def fine(self, value: int):
        if not isinstance(value, int):
            raise TypeError("Fine must be Integer")
        if value < 0:
            raise AttributeError("Penalty must be positive value")
        self._fine = value


@dataclass
class TelegramUser:
    """dataclass tg user. who send msg."""

    tg_id: int
    username: str
    first_name: str
    full_name: str
    language_code: str


@dataclass
class BetTimeTelegramUser:
    tg_user: TelegramUser = field(compare=False)
    bet_time1: int
    date_bet1: datetime = datetime.now()
    bet_time2: int = field(default=0)
    date_bet2: datetime = field(compare=False, default=datetime.now())
    delta_bet_time1: None = None

    def __setattr__(self, name, value):
        if name == "bet_time1" and value < 0:
            raise ValueError("bet_time1 cannot be negative")
        if name == "bet_time2" and value < 0:
            raise ValueError("bet_time2 cannot be negative")
        super().__setattr__(name, value)


if __name__ == "__main__":
    pass
