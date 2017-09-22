#!/usr/bin/python
# -*- coding: utf-8 -*-

import random
import numpy as np
import pandas as pd


class Card(object):
    suits = ['spade', 'club', 'heart', 'diam']

    def __init__(self, suit, number=1):
        self.suit = suit
        assert suit in self.suits or suit == 'JOKER'
        self.number = number
        assert 1 <= number <= 13 or number is None

    def __repr__(self):
        return '{}_{}'.format(self.suit, self.number) if self.suit != 'JOKER' else 'JOKER'

    def __eq__(self, other):
        return self.suit == other.suit and self.number == other.number

    def __hash__(self):
        return hash(self.number) + hash(self.suit)


class Agent(object):

    def __init__(self, index):
        self.index = index
        self.cards = set()
        self.next_ = None
        self.prev_ = None

    def draw(self, card):
        for c in self.cards:
            if card.number == c.number:
                self.cards.remove(c)
                break
        else:
            self.cards.add(card)

    def drawn(self):
        assert len(self.cards)
        card_ = random.sample(self.cards, 1)
        card = card_[0]
        self.cards.remove(card)
        return card

    def empty(self):
        return len(self.cards) == 0

    def __repr__(self):
        return 'Player_{}'.format(self.index)


class Game(object):

    __BEGIN__ = 0
    __PLAYING__ = 1
    __END__ = 2

    def __init__(self, n_people, verbose=False, serve_randomly=True, begin_randomly=True):
        """
        Parameters
        ----------
        n_people: 参加人数
        verbose
        serve_randomly : 配り始める位置をランダムにするか0からにするか
        begin_randomly : ターンを始める位置をランダムにするか0からにするか
        """
        self.n_people = n_people
        self.agents = [Agent(index=i) for i in range(n_people)]
        for i in range(n_people):
            if i == 0:
                self.agents[i].prev_ = self.agents[n_people - 1]
            else:
                self.agents[i].prev_ = self.agents[i - 1]

            if i == n_people - 1:
                self.agents[i].next_ = self.agents[0]
            else:
                self.agents[i].next_ = self.agents[i + 1]

        self.results = []
        self.now_agent = None
        self.status = self.__BEGIN__
        self.verbose = verbose
        self.serve_randomly = serve_randomly
        self.begin_randomly = begin_randomly

    def serve_cards(self):
        cards = []
        for suit in Card.suits:
            for number in range(1, 14):
                cards.append(Card(suit, number))
        cards.append(Card('JOKER'))

        random.shuffle(cards)

        if self.serve_randomly:
            now_agent = random.sample(self.agents, 1)[0]
        else:
            now_agent = self.agents[0]

        for card in cards:
            now_agent.draw(card)
            now_agent = now_agent.next_

        for i in range(self.n_people):
            if now_agent.empty():
                self.win_out(now_agent)
            now_agent = now_agent.next_

    def transaction(self):
        if len(self.agents) == 1:
            self.results.append(self.agents[0].index)
            self.status = self.__END__
            return

        card = self.now_agent.next_.drawn()
        if self.now_agent.next_.empty():
            self.win_out(self.now_agent.next_)

        self.now_agent.draw(card)
        if self.now_agent.empty():
            self.win_out(self.now_agent)

        self.now_agent = self.now_agent.next_

        self.status = self.__PLAYING__
        return

    def win_out(self, agent):
        if self.verbose:
            print('{} win!'.format(agent))
        agent.prev_.next_ = agent.next_
        agent.next_.prev_ = agent.prev_
        self.results.append(agent.index)
        self.agents.remove(agent)

    def play(self):
        self.serve_cards()

        # start!
        if self.begin_randomly:
            self.now_agent = random.sample(self.agents, 1)[0]
        else:
            self.now_agent = self.agents[0]

        self.status = self.__PLAYING__

        turn = 1
        while self.status != self.__END__:
            self.transaction()
            if self.verbose:
                print('turn:{} agent:{}'.format(turn, self.now_agent))
                self.dump_game_status()

            turn += 1

        self.dump_results()

    def dump_results(self):
        print('-'.join(map(str, self.results)))

    def dump_game_status(self):
        print('---------')
        for agent in self.agents:
            print('{}: {}'.format(agent, agent.cards))


def main():
    n_people = 9

    results = {p: [] for p in range(n_people)}

    for i in range(10000):
        game = Game(
            n_people=n_people,
            serve_randomly=True,
            begin_randomly=False
        )
        game.play()
        for n, p in enumerate(game.results):
            results[p].append(n)

    for p in results.keys():
        score = pd.Series(results[p]).value_counts()
        #score = np.array(results[p]).mean()
        print('{}: first: {}, last: {}'.format(p, score.ix[0], score.ix[n_people-1]))


if __name__ == '__main__':
    main()

