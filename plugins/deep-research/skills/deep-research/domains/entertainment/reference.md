# Entertainment Research Reference

## Query Patterns

### Pattern 1: Event discovery and verification
```
"[artist/event] tour [year]" site:songkick.com
"[artist/event] tour dates [year]"
"[artist/event] concert [city] [year]"
"[venue] upcoming events [year]"
"[festival name] [year] lineup"
"[artist] tickets" site:ticketmaster.com
```

### Pattern 2: Critical reception (film/TV)
```
"[title] review" site:rottentomatoes.com
"[title] review" site:metacritic.com
"[title] [year] reviews"
"[title] critic review aggregate"
"[title] audience score"
"best [genre] [year]"
```

### Pattern 3: Critical reception (music)
```
"[album/artist] review" site:pitchfork.com
"[album] review" site:albumoftheyear.org
"[album] review [year]"
"[artist] best albums ranked"
"best [genre] albums [year]"
```

### Pattern 4: Streaming availability
```
"[title] streaming where to watch"
"[title] netflix disney hbo"
"[title] streaming [country]"
"[artist/album] spotify apple music"
"new releases [platform] [month] [year]"
```

### Pattern 5: Gaming
```
"[game title] review" site:opencritic.com
"[game title] metacritic score"
"[game title] release date platforms"
"[game title] system requirements"
"best [genre] games [year]"
```

### Pattern 6: Local events
```
"[city] events [month] [year]"
"[city] concerts [month] [year]"
"[city] theater shows [year]"
"[city] festivals [year]"
"[city] what's on this week"
```

---

## Preferred Source Tiers

### Tier 1 — Official and authoritative
| Source | URL | Specialty | Language |
|---|---|---|---|
| Songkick | songkick.com | Concert discovery | EN |
| Bandsintown | bandsintown.com | Tour dates | EN |
| Rotten Tomatoes | rottentomatoes.com | Film/TV aggregate reviews | EN |
| Metacritic | metacritic.com | Multi-media aggregate reviews | EN |
| IMDb | imdb.com | Film/TV database | EN |
| Pitchfork | pitchfork.com | Music reviews | EN |
| AllMusic | allmusic.com | Music database | EN |
| Billboard | billboard.com | Music industry data | EN |
| OpenCritic | opencritic.com | Gaming aggregate reviews | EN |
| Variety | variety.com | Entertainment industry trade | EN |

### Tier 2 — Ticketing and booking
| Source | URL | Specialty | Region |
|---|---|---|---|
| Ticketmaster | ticketmaster.com / .se / .de | Tickets | Global |
| Eventim | eventim.de / .se | Tickets | DACH/Nordic |
| DICE | dice.fm | Tickets | EU/UK |
| AXS | axs.com | Tickets | US/UK |
| Biljett.nu | biljett.nu | Tickets | Sweden |
| Eventbrite | eventbrite.com | Events/tickets | Global |

### Tier 3 — Community and discovery
| Source | URL | Specialty | Language |
|---|---|---|---|
| Letterboxd | letterboxd.com | Film community reviews | EN |
| Rate Your Music | rateyourmusic.com | Music community ratings | EN |
| Album of the Year | albumoftheyear.org | Music review aggregator | EN |
| Time Out | timeout.com | Local event listings | EN |
| Resident Advisor | ra.co | Electronic music events | EN |

---

## WebFetch Prompts by Source Type

**For official venue/festival websites:**
"What events are scheduled at this venue? What are the dates, times, and ticket
prices? Is there information about accessibility, parking, or age restrictions?
What is the cancellation/refund policy?"

**For Songkick/Bandsintown tour pages:**
"What are the confirmed tour dates for this artist? What venues and cities are
listed? Are there links to official ticket sales? Are any dates marked as
sold out or cancelled?"

**For Rotten Tomatoes/Metacritic:**
"What is the critic score and audience score? How many reviews are included in each?
What is the critic consensus summary? What are the highest and lowest notable
reviews? What is the rating (PG, R, etc.)?"

**For music review sites (Pitchfork, NME):**
"What score was given? What are the key points of the review? How does the reviewer
contextualize this within the artist's discography? Are there comparisons to other
artists or albums?"

**For streaming platform pages:**
"Is this content available on this platform? Is it included with subscription or
rental/purchase only? What is the rental/purchase price? In what quality options
(HD, 4K, Dolby Atmos)? What are the available subtitle/audio languages?"

**For ticketing platforms:**
"What ticket tiers are available and at what prices? Is the event sold out? Is there
a resale/waiting list option? What is the refund policy? Are tickets digital or
physical? Is there a ticket transfer option?"

---

## Temporal Sensitivity

| Data type | Freshness requirement | Notes |
|---|---|---|
| Event dates | Current (< 1 week) | Events get cancelled/rescheduled |
| Ticket availability | Real-time | Sells out quickly |
| Streaming catalogs | Current (< 1 month) | Licensing changes monthly |
| Review scores | Stable after 2 weeks | New releases need time |
| Tour announcements | Current (< 1 month) | Tours get extended/cancelled |
| Festival lineups | Current season | Finalized months before event |
| Release dates | Current (< 1 month) | Delays common |

---

## Local-Language Query Patterns

### German
```
"[Kuenstler] Konzert [Stadt] [Jahr]"
"[Kuenstler] Tour [Jahr] Deutschland"
"[Veranstaltungsort] Programm [Monat]"
"[Stadt] Veranstaltungen [Monat] [Jahr]"
"[Film] Kinostart Deutschland"
```

### Swedish
```
"[artist] konsert [stad] [aar]"
"[artist] turne [aar] Sverige"
"[lokal] program [maanad]"
"[stad] evenemang [maanad] [aar]"
"[film] biopremiaar Sverige"
```

### French (for Francophone events)
```
"[artiste] concert [ville] [annee]"
"[festival] programmation [annee]"
"[ville] spectacles [mois] [annee]"
```
