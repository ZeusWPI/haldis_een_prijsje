from data_types.choice import ChoiceList, Choice, ChoiceType

############################
#        metropol          #
############################

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
    sauzen_keuze_list = ChoiceList(name="saus", description="Welke saus?")

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


def create_metropol_groenten_keuze_list():
    groenten_keuze_list = ChoiceList(name="groenten", description="Welke groenten?", type=ChoiceType.MULTI)

    alles = Choice("alle groenten")
    ajuun = Choice("ajuun")
    sla = Choice("sla")
    wortel = Choice("wortel")
    tomaat = Choice("tomaat")
    pikante_kruiden = Choice("pikante kruiden")
    zonder = Choice("zonder groenten")
    peper = Choice("peper", 0.50)
    frietjes = Choice("frietjes", 1.50)
    fetakaas = Choice("fetakaas", 1.00)
    mais = Choice("mais", 0.50)
    annanas = Choice("ananas", 0.50)
    cheddar = Choice("cheddar kaas", 0.50)
    gedroogde_ajuin = Choice("gedroogde ajuin", 0.50)
    mozarella = Choice("mozarella kaas", 3.00)
    sate_kruiden = Choice("sate kruiden", 0.50)
    coban_salta = Choice("coban salta")

    groenten_keuze_list.choices = [
        alles, zonder, peper, frietjes, fetakaas, mais, annanas, cheddar, sate_kruiden, coban_salta,
        gedroogde_ajuin, mozarella, pikante_kruiden, tomaat, fetakaas, ajuun, sla, wortel
    ]
    return groenten_keuze_list

def create_metropol_extra_keuze_list():
    extra_keuze_list = ChoiceList(name="extra", description="Welke extra's?", type=ChoiceType.MULTI)

    vlees = Choice("extra vlees", 3.00)
    saus = Choice("extra saus", 1.00)
    groenten = Choice("extra groenten", 1.00)

    extra_keuze_list.choices = [
        vlees, saus, groenten
    ]
    return extra_keuze_list
