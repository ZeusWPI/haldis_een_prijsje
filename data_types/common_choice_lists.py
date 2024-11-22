from data_types.choice import ChoiceList, Choice


# used in metropol
def create_metropol_vlees_keuze_list():
    vlees_keuze_list = ChoiceList(name="vlees", description="Welk vlees?")

    lam = Choice("lam")
    kip = Choice("kip")
    mix = Choice("mix", 0.5)
    kipfilet = Choice("kipfilet", 3.0)
    falafel = Choice("falafel")

    vlees_keuze_list.choices = [lam, kip, mix, kipfilet, falafel]
    return vlees_keuze_list

# used in metropol
def create_metropol_sauzen_keuze_list():
    sauzen_keuze_list = ChoiceList(name="Saus", description="Welk saus?")

    look = Choice("look")
    samurai = Choice("samurai")
    andalous = Choice("andalous")
    mayonais = Choice("mayonais")
    t_ketchup = Choice("T.ketchup")
    c_ketchup = Choice("C.ketchup")
    jopie = Choice("jopie")
    amerikan = Choice("amerikan")
    cocktail = Choice("Cocktail")
    harissa = Choice("harissa")
    mammoet = Choice("mammoet")
    tartaar = Choice("tartaar")
    bicky_geel = Choice("bicky_geel")
    bicky_rood = Choice("bicky_rood")
    frietsaus = Choice("frietsaus")
    pilipili = Choice("pilipili")
    brasil = Choice("brasil")
    zoetzuursaus = Choice("zoetzuursaus")
    cheesysaus = Choice("cheesysaus")
    sambal = Choice("sambal")
    tabasco = Choice("tabasco")
    pepersaus = Choice("pepersaus")
    geele_cury = Choice("geele_cury")
    bbq_saus = Choice("bbq_saus")
    algerian = Choice("algerian")
    stoofvlees_saus = Choice("stoofvlees_saus", 4.50)
    zonder_saus = Choice("zonder_saus")

    sauzen_keuze_list.choices = [
        look, samurai, andalous, mayonais, t_ketchup, c_ketchup, jopie, amerikan,
        cocktail, harissa, mammoet, tartaar, bicky_geel, bicky_rood, frietsaus, pilipili, brasil, zoetzuursaus,
        cheesysaus, sambal, tabasco, pepersaus, geele_cury, bbq_saus, algerian, stoofvlees_saus, zonder_saus
    ]
    return sauzen_keuze_list
