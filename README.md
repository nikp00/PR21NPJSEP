# Vmesno poročilo o opravljenem delu

Datum oddaje poročila: 6.4.2020

Avtorji:

- Nik Prinčič
- Jaka Škerjanc
- Erik Pahor

Mentor:

- izr. prof. dr. Tomaž Curk

## Opis Problema

Področje naše raziskave je trg kripto valut, bolj natančno kako pogovori na platformah kot sta Discord in Reddit, kjer si mnenja izmenjujeo predvsem kripto navdušenci, vplivajo na gibanje cen. Osredotočili se bomo predvsem na kriptovalute z nizko tržno kapitalizacijo (market cap).

Izbrane naloge, ki jih želimo raziskat:

- Ali lahko iz objav napovemo spremembo cene?
- Poiskati povezavo med ceno in popularnostjo na Reddit/Discord
- Ali kateri kovanci posebej izstopajo?
- Kako se je spreminajalo zanimanje za kripto valute?

## Pridobivanje podatkov

Podatke o objavah uporabnikov smo dobili na dveh platformah 
 
- Discord: Tri skupnosti kripto navdušencev skupno preko 130.000 članov. Za obdobje od 1.2.2021 do 31.3.2021 smo pridobili skupno 1.700.000 sporočil.
Ker Discord ne omogoča dostopa do sporočil preko kašnega vmesnika (npr. API), smo morali podatke pridobiti z programom [DiscordChatExporter](https://github.com/Tyrrrz/DiscordChatExporter), ki nam vrne .csv obliko. Da zmanjšamo velikost izbrišemo vse nepotrebne metapodatke. Na koncu nam ostane vsebina sporočila ter datum in čas.
- Reddit: Tukaj smo poiskali 4 "subreddite", kjer imajo vsak dan oziroma teden objavo v kateri uporabniki debatirajo o trenutno aktualnih zadevah. Pridobili smo komentarje iz 71 takih objav. Za to smo uporabili [PRAW: The Python Reddit API Wrapper](https://github.com/praw-dev/praw).

## Glavne ugotovitve

Trenutno smo še osredotočeni na pridobivanje čim več kvalitetnih podatkov, ki bodo v nadaljevanju osnova za uspešno iskanje odgovorov v podatkih.