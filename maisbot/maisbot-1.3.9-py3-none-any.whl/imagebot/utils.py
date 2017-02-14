

def confirma(pergunta):
    """Retorna S ou N"""
    resposta_ok = False
    while not resposta_ok:
        resposta = input("\n{} (s/n)? ".format(pergunta))
        if resposta and resposta[0].upper() in ["S", "N"]:
            resposta_ok = True
    return resposta[0].upper() == "S"