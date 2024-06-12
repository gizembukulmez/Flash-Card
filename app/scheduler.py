"""
Class that handles scheduling of the cardsa
"""
import datetime


class Scheduler:
    def __init__(self, cards):
        self.cards = cards

    def schedule_cards(self):
        """
        Schedule a card for review based on its parameters.
        Returns the cards after updating the next_review_date.
        """
        for card in self.cards:
            next_review_date = self.calculate_next_review_date(card)
            # Add next_review_date for the cards
            print(next_review_date)
            card.next_review_date = next_review_date
        return self.cards

    def calculate_next_review_date(self, card):
        """Basic scheduler algorithm: Calculate the next review date"""
        creation_date = card.timestamp
        # TODO: Check the default values once again
        right_count = card.flags.get("right", 0)
        wrong_count = card.flags.get("wrong", 0)
        # Calculated based on creation date and counts
        if wrong_count == 0:
            wrong_count = 1
        ratio = right_count / wrong_count
        interval_days = max(1, round(2 * ratio))  # 2 days as a base interval
        next_review_date = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=interval_days)
        return next_review_date

    def pick_cards(self):
        """
        Returns a list of cards to review today
        """
        today = datetime.datetime.now(datetime.timezone.utc).date()
        return [card for card in self.cards if card.next_review_date and card.next_review_date.date() <= today]
