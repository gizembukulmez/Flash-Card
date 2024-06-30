"""
Class that handles scheduling of the cardsa
"""
import datetime
from collections import defaultdict


class Scheduler:
    """
    Simple daily review card scheduler inspider by Leitner System
    """
    def __init__(self, cards):
        self.cards = cards
        self.box_intervals = [7, 4, 3, 2, 1]  # Review intervals in days (Intervals are split from 1 day -- 7 days interval) # Highest scoring cards are given lowest preference
        self.box_count = len(self.box_intervals)
        self.box_threshold = [80, 60, 40, 20, 0]  # Different score thresholds

    def schedule_cards(self):
        """
        Schedule card for review based in their parameters
        Returns updated cards list with next review date set
        """
        for card in self.cards:
            next_review_date = self.calculate_next_review_date(card)
            card.next_review_date = next_review_date
        return self.cards

    def calculate_next_review_date(self, card):
        """
        Calculate the next review date based on the card performance
        """
        current_box = self.determine_box(card)
        interval_days = self.box_intervals[current_box]
        next_review_date = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=interval_days)
        return next_review_date

    def calculate_score(self, card):
        """
        Calculates card score based on card's statistics
        """
        right = card.flags.get('right', 0)
        wrong = card.flags.get('wrong', 0)
        hints = card.flags.get('hints', 0)
        score = right * 10 - wrong * 5 - hints * 2
        return score

    def determine_box(self, card):
        """
        Determine which box to put a certain card into
        Args:
            Card object
        Returns:
            box_category : int
        """
        score = self.calculate_score(card)
        for i, threshold in enumerate(self.box_threshold):
            if score >= threshold:
                return i
        return self.box_count - 1

    def pick_card(self):
        """
        Picks the card's based on the cards passed to the scheduler object
        Args:
            Scheduler object
        Returns:
            Picked cards : list
        """
        today = datetime.datetime.now(datetime.timezone.utc).date()
        review_dates = defaultdict(list)
        for card in self.cards:
            if card.next_review_date and card.next_review_date.date() <= today:
                review_dates[card.next_review_date].append(card)
        if review_dates:
            picked_cards = []
            for date in sorted(review_dates.keys()):
                picked_cards.extend(review_dates[date])
            return picked_cards

        # IF NO CARDS ARE FOUND TO BE SCHEDULED FOR REVIEW ON A DAY
        # PICK A CARD FROM LEST SCORED BOX
        least_scored_cards = self.pick_from_least_scored_box()
        return least_scored_cards

    def pick_from_least_scored_box(self):
        """
        Picks card from the least scored box available
        Args:
            Scheduler Object
        Return:
            Least scored cards in the available boxes: list
        """
        least_scored_cards = []
        for card in self.cards:
            current_box = self.determine_box(card)
            if current_box == self.box_count - 1:  # Select the box_interval of last date __ or __
                least_scored_cards.append(card)
        # Sorting least_scored_cards by last review date (ascending) before picking
        least_scored_cards.sort(key=lambda x: x.timestamp or datetime.datetime.min)
        return least_scored_cards
