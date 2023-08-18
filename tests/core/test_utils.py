from newsroom.utils import short_highlighted_text


def test_short_highlighted_text():
    # Returns truncated text with highlighted span
    html = """<p>On olemassa myös sellaisia ihmisiä, joiden silmissä
jokainen parisuhde muuttuu huonoksi jo muutaman vuoden kuluessa.
Tällöin kyse voi olla siitä, etteivät he kestä suhteen arkipäiväistymistä,
kuvailee yksilö- ja pariterapeutti Jouni Pölönen.</p>


<p>Pölösen mukaanalkuhuuma <span class="es-highlight">kestää</span> yleensä 1–2 vuotta.
</p>

<p>–Suhteen alussa on usein paljon seksiä ja ihmiset tuovat parhaat puolensa esiin.
Kun suhde sitten arkipäiväistyy ja intohimo väistyy arjen tieltä</p>"""

    output = short_highlighted_text(html)
    assert output == 'Pölösen mukaanalkuhuuma <span class="es-highlight">kestää</span> yleensä 1–2 vuotta....'

    # Can output text only
    output = short_highlighted_text(html, output_html=False)
    assert output == "Pölösen mukaanalkuhuuma *kestää* yleensä 1–2 vuotta...."

    # Can truncate text without highlights
    html = """On olemassa myös sellaisia ihmisiä, joiden silmissä
jokainen parisuhde muuttuu huonoksi jo muutaman vuoden kuluessa.
Tällöin kyse voi olla siitä, etteivät he kestä suhteen arkipäiväistymistä,
kuvailee yksilö- ja pariterapeutti Jouni Pölönen."""
    output = short_highlighted_text(html, max_length=10)
    assert output == "On olemassa myös sellaisia ihmisiä, joiden silmissä jokainen parisuhde muuttuu..."

    # Returns truncated text with highlighted span at the beginning of the line
    html = """<p><span class="es-highlight">Turvattomuuden</span> kokemukset sen sijaan voivat
altistaa jatkossakin sille, että ihmissuhteet katkeavat herkemmin.
Kokemukset turvattomuudesta saattavat heikentää ihmisen kykyä
altistaa omaa ja toisen ihmisen mieltä.</p>"""
    output = short_highlighted_text(html)
    assert (
        output
        == """<span class="es-highlight">Turvattomuuden</span> kokemukset sen sijaan voivat
altistaa jatkossakin sille, että ihmissuhteet katkeavat herkemmin.
Kokemukset turvattomuudesta saattavat heikentää ihmisen kykyä
altistaa omaa ja toisen ihmisen mieltä...."""
    )

    # Returns truncated text with highlighted span inside a list
    html = """<ul><li>Foo</li><li><span class="es-highlight">Bar</span></li><li>Baz</li></ul>"""
    output = short_highlighted_text(html)
    assert output == '<span class="es-highlight">Bar</span>...'

    # Returns truncated text with highlighted span across different HTML tags
    html = """<p>part of a paragraph</p><h2>something and something else <span class="es-highlight">matching word</span></h2>"""
    output = short_highlighted_text(html)
    assert output == 'something and something else <span class="es-highlight">matching word</span>...'

    # Returns text if we search term is in long paragraph
    html = """<p>On olemassa myös sellaisia ihmisiä, joiden silmissä
jokainen parisuhde muuttuu huonoksi jo muutaman vuoden kuluessa.
Tällöin kyse voi olla siitä, etteivät he kestä suhteen arkipäiväistymistä,
kuvailee yksilö- ja pariterapeutti Jouni Pölönen mukaanalkuhuuma
<span class="es-highlight">kestää</span> yleensä 1–2 vuotta.
</p><p>–Suhteen alussa on usein paljon seksiä ja ihmiset tuovat parhaat puolensa esiin.
Kun suhde sitten arkipäiväistyy ja intohimo väistyy arjen tieltä</p>"""
    output = short_highlighted_text(html)
    assert (
        output
        == """On olemassa myös sellaisia ihmisiä, joiden silmissä
jokainen parisuhde muuttuu huonoksi jo muutaman vuoden kuluessa.
Tällöin kyse voi olla siitä, etteivät he kestä suhteen arkipäiväistymistä,
kuvailee yksilö- ja pariterapeutti Jouni Pölönen mukaanalkuhuuma <span class="es-highlight">kestää</span> yleensä 1–2 vuotta...."""
    )

    # Returns highlighted text if we have multiple words search term span together
    html = """<p>On olemassa myös sellaisia ihmisiä, joiden silmissä
jokainen parisuhde muuttuu <span class="es-highlight">mukaanalkuhuuma</span> <span class="es-highlight">kestää</span> yleensä 1–2 vuotta"""
    output = short_highlighted_text(html)
    assert (
        output
        == """On olemassa myös sellaisia ihmisiä, joiden silmissä
jokainen parisuhde muuttuu <span class="es-highlight">mukaanalkuhuuma</span>  <span class="es-highlight">kestää</span> yleensä 1–2 vuotta..."""
    )
