---
schema: course.v1

course:
  id: nukleare-sicherheit-vertiefung
  source_doc: "nukleare-sicherheit-intermediate.md"
  title: "Nukleare Sicherheit: Sicherheitsanalyse, Alterungsmanagement und Störfallmanagement"
  version: "1.0"
  provider: "Kurs-Team"
  language: German
  level: Fortgeschritten
  tags: [nukleare-sicherheit, sicherheitsanalyse, psa, alterungsmanagement, stoerfallmanagement, kerntechnik]
  estimated_minutes: 60
  published: true
  prerequisites: [nukleare-sicherheit-grundlagen]

instructors:
  - id: inst-1
    name: "Kurs-Team"
    bio: "Vertiefungskurs zu Sicherheitsfunktionen, deterministischen und probabilistischen Analysen, Alterungsmanagement sowie Accident Management in kerntechnischen Anlagen."

grading:
  pass_percent: 70
  assessment_weights:
    m1: 0.20
    m2: 0.20
    m3: 0.20
    final_quiz: 0.40
  policy:
    calculation:
      type: weighted_modules
      weights_ref: "grading.assessment_weights"
    completion:
      required_modules: [m1, m2, m3]
      required_assessments: [final-quiz]
      assessment_pass_percent: 70
    notes:
      - "Die Gesamtnote ist der gewichtete Mittelwert der Modul-Quiz-Ergebnisse und des Abschlussquizzes."
      - "Der Kurs baut auf dem Einsteigerkurs zur nuklearen Sicherheit auf."
      - "Alle drei Module sowie das Abschlussquiz müssen bestanden werden, um den Kurs abzuschließen."

resources:
  - id: res-1
    title: "IAEA Safety Fundamentals: Fundamental Safety Principles"
    type: pdf
    url: "https://www-pub.iaea.org/MTCD/Publications/PDF/Pub1273_web.pdf"
  - id: res-2
    title: "IAEA GSR Part 4 (Rev. 1): Safety Assessment for Facilities and Activities"
    type: pdf
    url: "https://www-pub.iaea.org/MTCD/Publications/PDF/Pub1714web-7976998.pdf"
  - id: res-3
    title: "IAEA SSR-2/1 (Rev. 1): Safety of Nuclear Power Plants: Design"
    type: pdf
    url: "https://www-pub.iaea.org/MTCD/Publications/PDF/Pub1715web-46541668.pdf"
  - id: res-4
    title: "IAEA Safety Guide: Accident Management Programmes for Nuclear Power Plants"
    type: pdf
    url: "https://www-pub.iaea.org/MTCD/Publications/PDF/Pub1376_web.pdf"
  - id: res-5
    title: "ENSREG Topical Peer Review Report: Ageing Management"
    type: pdf
    url: "https://www.ensreg.eu/sites/default/files/attachments/hlg_p2018-37_160_1st_topical_peer_review_report_2.pdf"
  - id: res-6
    title: "WENRA Safety Reference Levels for Existing Reactors (2020)"
    type: pdf
    url: "https://wenra.eu/sites/default/files/publications/wenra_safety_reference_level_for_existing_reactors_2020.pdf"
  - id: res-7
    title: "BfS: Radiologischer Notfallschutz"
    type: link
    url: "https://www.bfs.de/DE/themen/ion/notfallschutz/notfallschutz_node.html"
---

<!-- Course contents start -->

# Nukleare Sicherheit: Sicherheitsanalyse, Alterungsmanagement und Störfallmanagement

## Course overview

Dieser Kurs ist als **Fortsetzung** des Einsteigerkurses zur nuklearen Sicherheit konzipiert. Während der Grundlagenkurs die Ziele der nuklearen Sicherheit, Defence in Depth, physische Barrieren und den radiologischen Notfallschutz eingeführt hat, vertieft dieser Aufbaukurs die Frage, **wie Sicherheit systematisch analysiert, über den Lebenszyklus aufrechterhalten und bei auslegungsüberschreitenden Ereignissen beherrscht wird**.

Im Mittelpunkt stehen die grundlegenden Sicherheitsfunktionen kerntechnischer Anlagen, die deterministische und probabilistische Sicherheitsanalyse, das Alterungsmanagement sowie Maßnahmen des Accident Managements. Damit verschiebt sich der Fokus von den Grundprinzipien hin zur **methodischen Sicherheitsbewertung und kontinuierlichen Sicherheitsverbesserung**.

### Learning outcomes

- Die zentralen Sicherheitsfunktionen kerntechnischer Anlagen benennen und erläutern.
- Den Unterschied zwischen deterministischer und probabilistischer Sicherheitsanalyse erklären.
- Die Rolle von Alterungsmanagement und periodischer Sicherheitsüberprüfung einordnen.
- Den Begriff des schweren Störfalls und die Ziele des Accident Managements beschreiben.
- Die Schnittstelle zwischen anlageninternem Störfallmanagement und radiologischem Notfallschutz erklären.

## Modules

### Module 1: Sicherheitsfunktionen und deterministische Sicherheitsanalyse {#m1}

#### Content

##### Von Prinzipien zu Sicherheitsfunktionen

Im Einsteigerkurs wurde das allgemeine Sicherheitsziel beschrieben: der Schutz von Menschen und Umwelt vor schädlichen radiologischen Folgen. In der praktischen Auslegung und Bewertung kerntechnischer Anlagen wird dieses Ziel in **konkrete Sicherheitsfunktionen** übersetzt.

Zu den zentralen Sicherheitsfunktionen gehören insbesondere:

- die **Kontrolle der Reaktivität**,
- die **Abfuhr der Wärme** aus dem Reaktorkern und den sicherheitsrelevanten Systemen,
- die **Einschließung radioaktiver Stoffe**.

Diese Funktionen müssen nicht nur im Normalbetrieb, sondern auch bei Störungen und Störfällen mit hoher Zuverlässigkeit erhalten bleiben.

![Sicherheitsfunktionen und deterministische Bewertung von Anlagenzuständen.](/api/course/{{COURSE_ID}}/images/nuclear_safety_intermediate_course_1_safety_assessment.png)

##### Deterministische Sicherheitsanalyse

Die **deterministische Sicherheitsanalyse** untersucht, wie sich eine Anlage bei festgelegten Ereignissen und Randbedingungen verhält. Typische Ausgangsfragen sind:

- Welche auslösenden Ereignisse werden unterstellt?
- Welche Systeme müssen ihre Funktion erfüllen?
- Welche konservativen Annahmen sind anzusetzen?
- Werden Grenzwerte und Sicherheitskriterien eingehalten?

Dabei werden sogenannte **Auslegungsstörfälle** und weitere definierte Anlagenzustände betrachtet. Ziel ist es zu zeigen, dass die Anlage auch unter ungünstigen, aber systematisch angenommenen Bedingungen ihre Sicherheitsfunktionen erfüllt.

##### Wichtige Prinzipien in der Analyse

Zur deterministischen Sicherheitsbewertung gehören mehrere Grundprinzipien:

- **konservative Annahmen**, damit Risiken nicht unterschätzt werden,
- **Single-Failure-Gedanke**, damit der Ausfall einer einzelnen Komponente nicht zum Funktionsverlust führt,
- **Redundanz, Diversität und Trennung**, um gemeinsame Fehlerursachen zu begrenzen,
- **klare Akzeptanzkriterien**, damit Ergebnisse nachvollziehbar bewertet werden können.

Die deterministische Analyse beantwortet damit vor allem die Frage, ob die Anlage bei definierten Belastungen und Fehlerannahmen robust genug ausgelegt ist.

#### Questions (practice / free-response)

```yaml
- id: m1-q1
  prompt: "Nennen Sie die drei zentralen Sicherheitsfunktionen einer kerntechnischen Anlage."
  reference_answer: "Zu den zentralen Sicherheitsfunktionen gehören die Kontrolle der Reaktivität, die Abfuhr der Wärme und die Einschließung radioaktiver Stoffe."
  points: 1

- id: m1-q2
  prompt: "Was ist das Hauptziel einer deterministischen Sicherheitsanalyse?"
  reference_answer: "Sie soll zeigen, dass eine Anlage bei definierten Störungen, Störfällen und konservativen Randbedingungen ihre Sicherheitsfunktionen zuverlässig erfüllt."
  points: 1
```

#### Quiz (auto-graded)

```yaml
meta:
  id: m1-quiz
  title: "Module 1 quiz"
  pass_percent: 70
items:
  - id: m1-quiz1
    type: mcq
    prompt: "Welche Antwort beschreibt eine zentrale Sicherheitsfunktion am besten?"
    points: 1
    choices:
      - id: a1
        text: "Kontrolle der Reaktivität, Wärmeabfuhr und Einschließung radioaktiver Stoffe."
        correct: true
        feedback: "Richtig. Diese drei Funktionen stehen im Zentrum der nuklearen Sicherheit."
      - id: a2
        text: "Ausschließlich die Maximierung der elektrischen Leistung."
        correct: false
        feedback: "Falsch. Leistung ist kein Ersatz für Sicherheitsfunktionen."
      - id: a3
        text: "Nur die externe Notfallkommunikation."
        correct: false
        feedback: "Falsch. Notfallkommunikation ist wichtig, aber keine der grundlegenden anlageninternen Sicherheitsfunktionen."

  - id: m1-quiz2
    type: mcq
    prompt: "Was kennzeichnet eine deterministische Sicherheitsanalyse?"
    points: 1
    choices:
      - id: a1
        text: "Sie betrachtet definierte Ereignisse und prüft mit konservativen Annahmen, ob Sicherheitskriterien eingehalten werden."
        correct: true
        feedback: "Richtig. Genau das ist der Kern der deterministischen Sicherheitsanalyse."
      - id: a2
        text: "Sie verzichtet bewusst auf technische Annahmen."
        correct: false
        feedback: "Falsch. Technische und konservative Annahmen sind gerade zentral."
      - id: a3
        text: "Sie ersetzt die Auslegung der Anlage vollständig durch statistische Schätzungen."
        correct: false
        feedback: "Falsch. Die deterministische Analyse ist keine rein statistische Methode."
```

#### Further reading

- [IAEA GSR Part 4 (Rev. 1): Safety Assessment for Facilities and Activities](https://www-pub.iaea.org/MTCD/Publications/PDF/Pub1714web-7976998.pdf)
- [IAEA SSR-2/1 (Rev. 1): Safety of Nuclear Power Plants: Design](https://www-pub.iaea.org/MTCD/Publications/PDF/Pub1715web-46541668.pdf)

#### Common misconceptions

```yaml
- misconception: "Deterministische Sicherheitsanalyse bedeutet, dass alle realen Ereignisse exakt vorhergesagt werden können."
  correction: "Sie betrachtet definierte und systematisch ausgewählte Anlagenzustände mit konservativen Annahmen, nicht die vollständige Realität in all ihren Einzelheiten."

- misconception: "Wenn eine Anlage mehrere Systeme hat, ist eine Sicherheitsanalyse kaum noch nötig."
  correction: "Gerade komplexe und redundante Systeme müssen systematisch bewertet werden, um ihre Wirksamkeit unter Störfallbedingungen nachzuweisen."
```

#### Grade

```yaml
completion:
  required: true
  passing_percent: 70
grade_items:
  - id: m1-quiz
    points_total: 2
```

### Module 2: Probabilistische Sicherheitsanalyse, Alterungsmanagement und periodische Überprüfung {#m2}

#### Content

##### Warum probabilistische Analysen zusätzlich wichtig sind

Die deterministische Sicherheitsanalyse beantwortet viele Grundfragen, erfasst aber nicht jede denkbare Kombination von Fehlern und Wechselwirkungen. Deshalb wird sie durch die **probabilistische Sicherheitsanalyse (PSA)** ergänzt.

Die PSA untersucht unter anderem:

- welche Kombinationen von Ausfällen sicherheitsrelevant werden können,
- wie häufig bestimmte unerwünschte Anlagenzustände prinzipiell auftreten könnten,
- welche Systeme oder Abläufe besonders risikowichtig sind,
- wo Verbesserungsmaßnahmen die größte Wirkung entfalten.

Typischerweise unterscheidet man:

- **Level 1 PSA**: Analyse des Weges zu Kernschädigung,
- **Level 2 PSA**: Analyse der möglichen Freisetzungspfade und ihrer Beherrschung.

![Zusammenspiel von PSA, Alterungsmanagement und periodischer Sicherheitsüberprüfung.](/api/course/{{COURSE_ID}}/images/nuclear_safety_intermediate_course_2_psa_ageing.png)

##### Alterungsmanagement

Sicherheit ist keine einmalige Eigenschaft einer Anlage. Werkstoffe, Komponenten und Systeme verändern sich im Laufe der Zeit. Deshalb ist **Alterungsmanagement** ein eigenständiger und zentraler Teil der nuklearen Sicherheit.

Zu berücksichtigen sind zum Beispiel:

- Materialermüdung,
- Korrosion,
- thermische und mechanische Belastungen,
- Versprödung,
- Obsoleszenz von Komponenten, Mess- und Leittechnik.

Ein wirksames Alterungsmanagement kombiniert Zustandsüberwachung, wiederkehrende Prüfungen, Instandhaltung, Austauschstrategien und die systematische Auswertung von Betriebserfahrung.

##### Periodische Sicherheitsüberprüfung

Neben der laufenden Überwachung spielen **periodische Sicherheitsüberprüfungen** eine wichtige Rolle. Dabei wird die Anlage in größeren Abständen umfassend daraufhin bewertet,

- ob sie noch dem Stand von Wissenschaft und Technik entspricht,
- welche neuen Erkenntnisse aus Forschung, Betriebserfahrung oder internationalen Ereignissen zu berücksichtigen sind,
- welche angemessenen Sicherheitsverbesserungen möglich und erforderlich sind.

Dieses Prinzip spiegelt die Grundidee der **kontinuierlichen Verbesserung** wider: Nukleare Sicherheit ist kein statischer Zustand, sondern ein fortlaufender Lern- und Anpassungsprozess.

#### Questions (practice / free-response)

```yaml
- id: m2-q1
  prompt: "Warum ergänzt die probabilistische Sicherheitsanalyse die deterministische Sicherheitsanalyse?"
  reference_answer: "Weil sie zusätzliche Informationen über Kombinationen von Ausfällen, risikowichtige Systeme und die relative Bedeutung verschiedener Störfallpfade liefert."
  points: 1

- id: m2-q2
  prompt: "Welche Ziele verfolgt ein systematisches Alterungsmanagement?"
  reference_answer: "Es soll sicherstellen, dass sicherheitsrelevante Strukturen, Systeme und Komponenten trotz Alterung, Belastung und Obsoleszenz ihre Funktionen zuverlässig erfüllen."
  points: 1
```

#### Quiz (auto-graded)

```yaml
meta:
  id: m2-quiz
  title: "Module 2 quiz"
  pass_percent: 70
items:
  - id: m2-quiz1
    type: mcq
    prompt: "Welche Aussage zur probabilistischen Sicherheitsanalyse ist richtig?"
    points: 1
    choices:
      - id: a1
        text: "Sie ergänzt die deterministische Analyse durch die Betrachtung von Kombinationen von Ausfällen und ihrer relativen Bedeutung."
        correct: true
        feedback: "Richtig. Genau darin liegt ihr zusätzlicher Erkenntniswert."
      - id: a2
        text: "Sie macht deterministische Analysen überflüssig."
        correct: false
        feedback: "Falsch. Beide Ansätze ergänzen sich."
      - id: a3
        text: "Sie betrachtet ausschließlich den Normalbetrieb ohne Fehlerszenarien."
        correct: false
        feedback: "Falsch. Gerade Fehlerszenarien und ihre Kombinationen stehen im Mittelpunkt."

  - id: m2-quiz2
    type: mcq
    prompt: "Was gehört typischerweise zum Alterungsmanagement?"
    points: 1
    choices:
      - id: a1
        text: "Wiederkehrende Prüfungen, Zustandsüberwachung, Instandhaltung und Austauschstrategien."
        correct: true
        feedback: "Richtig. Diese Maßnahmen sind Kernelemente des Alterungsmanagements."
      - id: a2
        text: "Der Verzicht auf Inspektionen, solange der Normalbetrieb stabil erscheint."
        correct: false
        feedback: "Falsch. Gerade systematische Prüfungen sind entscheidend."
      - id: a3
        text: "Ausschließlich die Optimierung wirtschaftlicher Laufzeiten."
        correct: false
        feedback: "Falsch. Die Priorität liegt auf dem Erhalt der Sicherheitsfunktionen."
```

#### Further reading

- [ENSREG Topical Peer Review Report: Ageing Management](https://www.ensreg.eu/sites/default/files/attachments/hlg_p2018-37_160_1st_topical_peer_review_report_2.pdf)
- [WENRA Safety Reference Levels for Existing Reactors (2020)](https://wenra.eu/sites/default/files/publications/wenra_safety_reference_level_for_existing_reactors_2020.pdf)

#### Common misconceptions

```yaml
- misconception: "Eine probabilistische Sicherheitsanalyse liefert exakte Vorhersagen für konkrete reale Unfälle."
  correction: "Die PSA ist ein Modellierungs- und Bewertungsinstrument zur relativen Risikoeinordnung und zur Identifikation wichtiger Schwachstellen und Verbesserungspotenziale."

- misconception: "Alterungsmanagement ist nur bei sehr alten Anlagen relevant."
  correction: "Alterungsmechanismen beginnen nicht erst am Ende der Lebensdauer; sie müssen während des gesamten Betriebs überwacht und bewertet werden."
```

#### Grade

```yaml
completion:
  required: true
  passing_percent: 70
grade_items:
  - id: m2-quiz
    points_total: 2
```

### Module 3: Schwere Störfälle, Accident Management und Schnittstelle zum Notfallschutz {#m3}

#### Content

##### Was ist ein schwerer Störfall?

Ein **schwerer Störfall** ist ein Ereignis, bei dem es zu einer erheblichen Schädigung des Brennstoffs oder des Reaktorkerns kommen kann oder gekommen ist. Solche Situationen liegen typischerweise **jenseits der ursprünglichen Auslegungsannahmen** und erfordern besondere Strategien zur Schadensbegrenzung.

Schwere Störfälle unterscheiden sich von klassischen Auslegungsstörfällen dadurch, dass nicht mehr nur die Einhaltung der ursprünglichen Auslegungskriterien im Vordergrund steht, sondern die **Begrenzung von Kernschädigung und Freisetzung**.

##### Accident Management

Das **Accident Management** umfasst vorbereitete technische, organisatorische und prozedurale Maßnahmen, um auch bei schweren und auslegungsüberschreitenden Ereignissen die Folgen zu begrenzen. Dazu gehören unter anderem:

- symptomorientierte Notfall- und Störfallprozeduren,
- Strategien zur Erhaltung oder Wiederherstellung der Kühlung,
- Maßnahmen zur Begrenzung von Wasserstoffrisiken,
- organisatorische Unterstützung durch Notfallstäbe,
- Nutzung zusätzlicher oder alternativer Hilfsmittel bei Verlust regulärer Systeme.

![Accident Management und Übergang vom anlageninternen Management zum externen Notfallschutz.](/api/course/{{COURSE_ID}}/images/nuclear_safety_intermediate_course_3_severe_accident_management.png)

##### Schnittstelle zum radiologischen Notfallschutz

Anlageninternes Accident Management und **radiologischer Notfallschutz** außerhalb der Anlage sind eng miteinander verbunden, aber nicht identisch.

- Das **Accident Management** zielt primär darauf ab, den Anlagenzustand zu stabilisieren und Freisetzungen zu vermeiden oder zu begrenzen.
- Der **radiologische Notfallschutz** zielt darauf ab, die Bevölkerung und Einsatzkräfte durch vorbereitete Maßnahmen zu schützen, falls eine Freisetzung droht oder bereits eingetreten ist.

Zwischen beiden Ebenen sind deshalb schnelle Lageerkennung, belastbare Mess- und Prognosedaten, klare Kommunikationswege und abgestimmte Entscheidungsprozesse entscheidend.

##### Lernen aus Ereignissen

Ein zentrales Merkmal fortgeschrittener nuklearer Sicherheit ist das systematische Lernen aus Ereignissen, Übungen und internationalen Reviews. Gerade schwere Reaktorunfälle haben weltweit zu Anpassungen in Auslegung, Notfallvorsorge, Ausfallvorsorge, Unfallmanagement und regulatorischer Bewertung geführt.

#### Questions (practice / free-response)

```yaml
- id: m3-q1
  prompt: "Worin unterscheidet sich ein schwerer Störfall von einem klassischen Auslegungsstörfall?"
  reference_answer: "Bei einem schweren Störfall steht die Beherrschung einer erheblichen Kern- oder Brennstoffschädigung und die Begrenzung von Freisetzungen im Vordergrund; er liegt typischerweise jenseits der ursprünglichen Auslegungsannahmen."
  points: 1

- id: m3-q2
  prompt: "Warum ist die Schnittstelle zwischen Accident Management und radiologischem Notfallschutz so wichtig?"
  reference_answer: "Weil anlageninterne Maßnahmen und externe Schutzmaßnahmen zeitlich und inhaltlich abgestimmt werden müssen, um Freisetzungen zu begrenzen und die Bevölkerung wirksam zu schützen."
  points: 1
```

#### Quiz (auto-graded)

```yaml
meta:
  id: m3-quiz
  title: "Module 3 quiz"
  pass_percent: 70
items:
  - id: m3-quiz1
    type: mcq
    prompt: "Welches Ziel hat Accident Management in erster Linie?"
    points: 1
    choices:
      - id: a1
        text: "Den Anlagenzustand auch bei schweren Ereignissen zu stabilisieren und Freisetzungen zu begrenzen."
        correct: true
        feedback: "Richtig. Genau das ist die Kernaufgabe des Accident Managements."
      - id: a2
        text: "Ausschließlich die Öffentlichkeitsarbeit der Betreiber zu organisieren."
        correct: false
        feedback: "Falsch. Kommunikation ist wichtig, aber nicht die Hauptfunktion des Accident Managements."
      - id: a3
        text: "Den radiologischen Notfallschutz vollständig zu ersetzen."
        correct: false
        feedback: "Falsch. Accident Management und Notfallschutz ergänzen einander."

  - id: m3-quiz2
    type: mcq
    prompt: "Welche Aussage beschreibt die Schnittstelle zum radiologischen Notfallschutz korrekt?"
    points: 1
    choices:
      - id: a1
        text: "Anlageninterne Maßnahmen und externe Schutzmaßnahmen müssen abgestimmt sein."
        correct: true
        feedback: "Richtig. Nur so können Lagebewertung und Schutzmaßnahmen wirksam ineinandergreifen."
      - id: a2
        text: "Zwischen beiden Bereichen besteht keine operative Verbindung."
        correct: false
        feedback: "Falsch. Die Verbindung ist zentral für eine wirksame Ereignisbewältigung."
      - id: a3
        text: "Radiologischer Notfallschutz beginnt erst, wenn alle anlageninternen Maßnahmen beendet sind."
        correct: false
        feedback: "Falsch. Beide Bereiche können parallel relevant werden."
```

#### Further reading

- [IAEA Safety Guide: Accident Management Programmes for Nuclear Power Plants](https://www-pub.iaea.org/MTCD/Publications/PDF/Pub1376_web.pdf)
- [BfS: Radiologischer Notfallschutz](https://www.bfs.de/DE/themen/ion/notfallschutz/notfallschutz_node.html)

#### Common misconceptions

```yaml
- misconception: "Ein schwerer Störfall ist einfach nur ein besonders großer normaler Störfall."
  correction: "Schwere Störfälle bilden eine eigene sicherheitstechnische Kategorie, weil erhebliche Kern- oder Brennstoffschädigungen und besondere Accident-Management-Maßnahmen relevant werden."

- misconception: "Accident Management und radiologischer Notfallschutz meinen dasselbe."
  correction: "Accident Management ist primär anlagenintern und zustandsorientiert; radiologischer Notfallschutz richtet sich auf den Schutz von Bevölkerung und Einsatzkräften außerhalb der Anlage."
```

#### Grade

```yaml
completion:
  required: true
  passing_percent: 70
grade_items:
  - id: m3-quiz
    points_total: 2
```

## Overall Quiz

```yaml
meta:
  id: final-quiz
  title: "Abschlussquiz"
  points_total: 4
  pass_percent: 70
items:
  - id: final-quiz1
    type: true_false
    prompt: "Die deterministische Sicherheitsanalyse arbeitet mit definierten Anlagenzuständen und konservativen Annahmen."
    points: 1
    answer: true

  - id: final-quiz2
    type: true_false
    prompt: "Die probabilistische Sicherheitsanalyse ersetzt die deterministische Sicherheitsanalyse vollständig."
    points: 1
    answer: false

  - id: final-quiz3
    type: true_false
    prompt: "Alterungsmanagement dient dazu, den Erhalt sicherheitsrelevanter Funktionen über die Betriebszeit hinweg sicherzustellen."
    points: 1
    answer: true

  - id: final-quiz4
    type: true_false
    prompt: "Accident Management und radiologischer Notfallschutz sind unterschiedliche, aber eng gekoppelte Elemente des Sicherheitskonzepts."
    points: 1
    answer: true
```

<!-- Course contents End -->
