# Sports & Fitness — Search & Source Reference

## Query Patterns by Topic Type

### Training Science Queries
```
"[exercise/method] evidence-based [sport/goal]"
"[exercise/method] systematic review meta-analysis"
"[training method] peer reviewed research [year]"
"ACSM guidelines [topic] [year]"
"NSCA position statement [topic]"
"[exercise] proper form technique"
"[training program] periodization [level]"
"progressive overload [sport/goal] program"
"[exercise] EMG activation study"
"[sport] strength training program [level]"
"[sport] conditioning program off-season"
```

### Injury Prevention Queries
```
"[sport] common injuries prevention"
"[body part] injury prevention exercises [sport]"
"[injury type] return to sport protocol"
"[sport] warm-up routine evidence-based"
"[exercise] contraindications risk factors"
"BJSM [injury type] prevention [year]"
"[sport] overtraining syndrome signs"
"[body part] prehab exercises [sport]"
"[injury] recovery timeline sport"
"ACL injury prevention program [sport]"
```

### Spectator Statistics Queries
```
"[player name] career statistics"
"[team] [season] results standings"
"[league] [statistic] leaders [season]"
"[league] all-time records [category]"
"[player] vs [player] comparison stats"
"[team] transfer history [window/year]"
"[league] standings table [date]"
"[event/tournament] results [year]"
"[player] advanced metrics [platform]"          → e.g., xG, WAR, EPA
"[league] rule changes [year] impact"
```

### Event and Participation Queries
```
"[event/race] registration requirements [year]"
"[sport] beginner guide how to start"
"[sport] clubs near [location]"
"[event] qualification standards [year]"
"[sport] age group categories"
"[event] course route elevation [year]"
"[sport] equipment rules regulations"
"[event] schedule dates [year]"
"[sport] federation membership requirements"
```

### Equipment Queries
```
"best [equipment type] for [sport] [year]"
"[equipment A] vs [equipment B] [sport]"
"[equipment type] sizing guide [sport]"
"[equipment] technology comparison [year]"
"[sport] equipment rules regulations [governing body]"
"[equipment] durability review long-term"
"[equipment type] beginner vs advanced"
"[sport] essential gear checklist"
```

### Nutrition for Sport Queries
```
"sports nutrition [sport/goal] evidence-based"
"[nutrient/supplement] performance research"
"pre-workout nutrition timing evidence"
"post-workout recovery nutrition research"
"hydration guidelines [sport] [conditions]"
"ISSN position stand [supplement/nutrient]"
"[supplement] systematic review efficacy"
"endurance nutrition strategy [sport]"
"protein requirements [sport/goal] research"
```

## Preferred Source Tiers

### Tier 1 — Always search and prefer
| Source Type | Examples | Use For |
|---|---|---|
| Sports science journals | BJSM, MSSE, JSCR, Sports Medicine | Training methods, injury prevention |
| Official governing bodies | FIFA.com, NBA.com, WorldAthletics.org, IOC | Rules, records, official results |
| Sports science organizations | ACSM, NSCA, ISSN | Position statements, guidelines |
| Anti-doping authorities | WADA, USADA | Banned substances, testing protocols |
| Statistical databases | Basketball-Ref, FBref, Baseball-Ref | Verified statistics, historical data |

### Tier 2 — Good secondary sources
| Source Type | Examples | Use For |
|---|---|---|
| Quality sports journalism | ESPN, The Athletic, BBC Sport | News, analysis, transfers |
| Analytics platforms | FiveThirtyEight, Transfermarkt, Understat | Advanced metrics, valuations |
| Established training resources | NSCA publications, coaching textbooks | Training programs, technique |
| Sports medicine sites | AOSSM patient resources, BJSM blogs | Injury info for athletes |
| Equipment review outlets | RunRepeat, GearJunkie (with testing) | Equipment comparisons |

### Tier 3 — Use with caution
| Source Type | Examples | Caveat |
|---|---|---|
| Fitness communities | r/Fitness, r/running, Letsrun | Verify against evidence; experience-based |
| Training influencers | YouTube coaches with credentials | Check certifications, verify claims |
| Supplement review sites | Examine.com (evidence-rated) | Note funding and evidence grades |
| Fantasy/betting analytics | Various | Data may be valid but context is wagering |
| Fitness magazines | Men's Health, Shape | Often simplified; check cited sources |

## WebFetch Prompts by Source Type

**For sports science journal articles:**
"What are the study design, sample size, key findings, and effect sizes reported?
Include the population studied (elite vs recreational, age, sex), the intervention
protocol, and the authors' stated limitations."

**For official league/governing body pages:**
"What specific statistics, standings, results, or rules are presented on this page?
Include dates, matchday/round numbers, and any notes about data completeness or
official status."

**For sports analytics platforms:**
"What specific metrics, rankings, or analytical findings does this page present?
Include the methodology or model used, the time period covered, and any caveats
about the data (e.g., expected vs actual, model confidence)."

**For training program pages:**
"What is the training program structure, including sets, reps, frequency, progression
model, and periodization approach? What level is it designed for? Does the author
cite any evidence or credentials? Are there safety considerations mentioned?"

**For equipment review pages:**
"What specific equipment is reviewed, what testing methodology was used, and what are
the ratings or rankings? Include price points with dates, durability observations,
and the reviewer's stated experience level and testing duration."

**For sports journalism articles:**
"What are the key facts, quotes, and data points in this article? Distinguish between
confirmed information (official announcements, verified statistics) and speculation
or unnamed sources. Note the publication date."

**For injury/rehabilitation pages:**
"What specific injury mechanism, prevention strategies, or rehabilitation protocols
does this page describe? Include timelines, exercise progressions, and return-to-sport
criteria. Note whether the source is from a medical professional or sports scientist."

## Temporal Sensitivity Rules

| Topic | Sensitivity | Guidance |
|---|---|---|
| League standings/results | Real-time (daily during season) | Always note the date of data |
| Transfer news | Highly volatile (hourly during windows) | Distinguish confirmed vs rumored |
| Training science | Stable (years) | Note landmark studies; check for recent meta-analyses |
| Player statistics | Season-by-season | Note season and games played |
| Equipment models | Annual product cycles | Note model year |
| Anti-doping regulations | Updated annually (prohibited list) | Always cite current year's list |
| Rules and regulations | Updated periodically by governing body | Note effective date |
| Event schedules | Set annually, subject to change | Verify against official source |
| Supplement research | Evolving (check latest reviews) | Note most recent systematic review date |
| Coaching certifications | Periodic updates | Verify current requirements with issuing body |
