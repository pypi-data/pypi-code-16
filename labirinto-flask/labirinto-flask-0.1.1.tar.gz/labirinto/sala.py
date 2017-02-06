# -*- coding: utf-8 -*-

import yaml


class Sala:
    """Uma sala do labirinto, com um texto dica e as portas existentes, cada uma
    levando a outra sala"""
    def __init__(self, num, dica, portas, titulo=None):
        self.num = num
        self.dica = dica
        self.portas = portas
        self.titulo = titulo or "Sala {0}".format(num)

    def __repr__(self):
        return 'Sala({0.num}, {0.dica!r}, {0.portas!r}, {0.titulo!r})'.format(self)

    def porta_proxima(self, nome):
        """Acha qual o proximo passo a partir da porta"""
        # Usa `for` retornando o primeiro elemento pra funcionar tanto no python 2 quanto 3
        for porta in filter(lambda p: p['nome'] == nome, self.portas):
            return porta['proxima']


def get_salas():
    """Le o documento de salas e retorna a lista das salas existentes"""
    with open('salas.yml', 'r') as arq:
        return [Sala(num=i, **sala) for i, sala in enumerate(yaml.load(arq))]
