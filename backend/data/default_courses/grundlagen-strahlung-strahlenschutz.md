---
schema: course.v1 # Schema identifier

# course: course-level metadata stored in DB; used for catalog, search, routing, and page header
course: # Root course metadata object
  id: grundlagen-strahlung-strahlenschutz # Stable primary key
  source_doc: "grundlagen-strahlung-strahlenschutz.md" # Source file
  title: "Grundlagen Strahlung und Strahlenschutz" # Display title (catalog + course page)
  version: "1.1" # Content version for cache invalidation and audit/history
  provider: "Technische Universität München (TUM), ZTWB Radiochemie München RCM" # Display provider/partner label
  language: German # Locale for UI + future i18n filtering
  level: Einsteiger # Difficulty label for learners
  tags: [
      strahlung,
      strahlenschutz,
      ionisierende-strahlung,
      physikalische-grundlagen,
    ] # Search/filter facets
  estimated_minutes: 60 # Total course completion time
  published: true # Whether learners can access/see the course
  prerequisites: [] # Canonical prereqs list

# instructors: rendered on “Course info” and used for attribution/contact
instructors: # List of instructors (can support multiple)
  - id: inst-1 # Stable instructor id (joins to instructor table)
    name: "Prof. Thomas" # Display name
    bio: "Einführungskurs zu physikalischen Grundlagen von Strahlung und wesentlichen Konzepten des Strahlenschutzes." # Short profile text

# grading: used to compute grades and gate completion/certification
grading: # Root grading configuration
  pass_percent: 70 # Default pass threshold (course-level)
  assessment_weights: # Assessments Weights for module and final quizzes in final grade (must sum to 1.0)
    m1: 0.15 # Module 1 contribution to final grade
    m2: 0.15 # Module 2 contribution to final grade
    m3: 0.15 # Module 3 contribution to final grade
    m4: 0.15 # Module 4 contribution to final grade
    final_quiz: 0.40 # Final quizzes contribution to final grade 
  policy: # Optional policy block for display + backend rules
    calculation: # How grade is computed
      type: weighted_modules # Strategy identifier (backend dispatch key)
      weights_ref: "grading.assessment_weights" # Pointer to weights for DRY configuration
    completion:
      required_modules: [m1, m2, m3, m4]
      required_assessments: [final-quiz] # must be completed/passed
      assessment_pass_percent: 70 # threshold for required_assessments
    notes: # Human-readable grade explanation shown to learners
      - "Die Gesamtnote ist der gewichtete Mittelwert der Modul-Quiz-Ergebnisse." # UI copy
      - "Alle Module sowie das Abschlussquiz müssen bestanden werden, um den Kurs abzuschließen." # UI copy

# resources: rendered in “Resources”; also used for link cards/downloads
resources: # Course-wide resources list
  - id: res-1 # Stable resource id
    title: "Strahlenschutzgesetz (StrlSchG)" # Display label
    type: link # Resource type for icon/handling (pdf/link/video/etc.)
    url: "https://www.gesetze-im-internet.de/strlschg/" # Resource link
  - id: res-2
    title: "FAQ: Was ist ionisierende Strahlung?"
    type: pdf
    url: "https://www.fs-ev.org/fileadmin/user_upload/80_FAQs/strahlung_und_dosis/Frage_Nr_104.pdf"
  - id: res-3
    title: "FAQ: Wie wirken sich ionisierende Strahlen auf den Menschen aus?"
    type: pdf
    url: "https://www.fs-ev.org/fileadmin/user_upload/80_FAQs/strahlung_und_dosis/Frage_Nr_102.pdf"
  - id: res-4
    title: "FAQ: Natürliche Strahlung – was gibt es und wieviel?"
    type: pdf
    url: "https://www.fs-ev.org/fileadmin/user_upload/80_FAQs/strahlung_und_dosis/Frage_Nr_105.pdf"
---

<!-- Course contents start -->

# Grundlagen Strahlung und Strahlenschutz 

## Course overview

Der Kurs **Grundlagen Strahlung und Strahlenschutz** behandelt die wichtigsten Aspekte des Strahlenschutzes, deren Kenntnis für Tätigkeiten mit radioaktiven Stoffen zumindest erforderlich sind.

Es werden zunächst die physikalischen Grundlagen erläutert (Atome/Atomkerne), anschließend Strahlungsarten und Reichweiten sowie die Wechselwirkung ionisierender Strahlung mit Materie. Darauf aufbauend werden zentrale Begriffe und Denkmodelle vermittelt, die für Strahlenschutzmaßnahmen benötigt werden.

### Learning outcomes

- Den Begriff „Tätigkeit“ im Sinne des Strahlenschutzgesetzes einordnen und den Kursaufbau verstehen.
- Aufbau von Atomen und Atomkernen erklären (inkl. Nukleonen, Nuklide, Isotope) und Beispiele geben.
- Strahlung und ionisierende Strahlung definieren; grundlegende Strahlungsarten (α, β, Photonen, Neutronen) unterscheiden.
- Elektronenvolt als Energieeinheit nutzen und typische Energiebereiche verschiedener Strahlungsarten einordnen.
- Grundprinzipien der Wechselwirkung von Strahlung mit Materie erklären (direkt/indirekt ionisierend, Photoeffekt, Compton, Paarbildung) sowie Schwächung qualitativ verstehen.

## Modules

### Module 1: 1_Einleitung und Lernziele {#m1}

#### Content

Der Kurs **Grundlagen des Strahlenschutzes** behandelt die wichtigsten Aspekte des Strahlenschutzes, deren Kenntnis für Tätigkeiten mit radioaktiven Stoffen **zumindest** erforderlich sind.

**\*Anmerkung:**
Als Tätigkeit wird gemäß § 4, Absatz 1, Strahlenschutzgesetz (StrlSchG) unter anderem der Umgang (§ 5, Abs. 39, StrlSchG) in Form von Erzeugung, Lagerung, Bearbeitung, Verarbeitung und sonstiger Verwendung und Beseitigung von\*

- _künstlich erzeugten radioaktiven Stoffen und_
- _natürlich vorkommenden radioaktiven Stoffen aufgrund ihrer Radioaktivität, zur Nutzung als Kernbrennstoff oder zur Erzeugung von Kernbrennstoffen_

_verstanden._

Es werden zuerst die physikalischen Grundlagen, welche für die Behandlung dieses Themas erforderlich sind, erklärt. Im Anschluss an eine kurze Beschreibung des Aufbaus von Atomen und Atomkernen, werden die verschiedenen Strahlungsarten erläutert sowie auf die Wechselwirkung ionisierender Strahlung mit Materie eingegangen.

Ein zentraler Punkt für eine optimale Auslegung von Strahlenschutzmaßnahmen ist die Kenntnis der Strahlenwirkung auf biologische Organismen. Dies wird durch eine vertiefte Betrachtung der biologischen Wirkung ionisierender Strahlung im Allgemeinen und der Strahlenwirkung auf den menschlichen Organismus im Speziellen behandelt. Die hieraus resultierende Strahlenexposition auf den Menschen werden betrachtet.

Basierend auf den vorgenannten Aspekten leiten sich Regeln und Maßnahmen des Strahlenschutzes ab, die in Strahlenschutzgrundsätzen und Vorsorgemaßnahmen im Strahlenschutz resultieren. Diese betreffen unter anderem den Umgang mit radioaktiven Stoffen, Maßnahmen bei Kontamina-tion, Inkorporation und Dekontamination, die Definition und Kennzeichnung von Strahlenschutzbereichen, den Bereich der beruflich strahlenexponierten Personen sowie die Dosimetrie und Dosisgrenzwerte.

#### Questions (practice / free-response)

```yaml
- id: m1-q1 # Unique item id (stable; used for attempts/history)
  prompt: "In welchem Paragraphen des Strahlenschutzgesetzes wird der Begriff der Tätigkeit definiert?" # Question text
  reference_answer: "Der Begriff der Tätigkeit wird in § 4 Strahlenschutzgesetz (StrlSchG) definiert." # Prof. solution
  points: 1 # Points if you choose to grade it

- id: m1-q2
  prompt: "Nennen Sie einen zentralen Punkt für eine optimale Auslegung von Strahlenschutzmaßnahmen."
  reference_answer: "Ein zentraler Punkt für eine optimale Auslegung von Strahlenschutzmaßnahmen ist die Kenntnis der Strahlenwirkung auf biologische Organismen."
  points: 1
```

#### Quiz (auto-graded)

```yaml
meta:
  id: m1-quiz
  title: "Module 1 quiz"
  pass_percent: 70
items:
  - id: m1-quiz1 # Unique quiz item id
    type: multi_select # Item type for renderer/grader
    prompt: "Was wird unter dem Begriff Tätigkeit gemäß § 4 Strahlenschutzgesetz (StrlSchG) verstanden?"
    points: 1
    choices: # Choices list for MCQ
      - id: a1
        text: "Die Lagerung von radioaktiven Stoffen mit einer hohen Radioaktivität."
        correct: true
        feedback: "Ihre Antwort ist korrekt."
      - id: a2
        text: "Das Experimentieren mit radioaktiven Stoffen über der Freigrenze in einem radiochemischen Labor."
        correct: true
        feedback: "Ihre Antwort ist korrekt."
      - id: a3
        text: "Das Erstellen einer Dokumentation in einem Kernbrennstofflabor mit einer Umgangsgenehmigung nach Atomgesetz."
        correct: false
        feedback: "Ihre Antwort ist falsch. Der Begriff der Tätigkeit bezieht sich auf radioaktive Stoffe und Kernbrennstoffe. Die Nutzung von nicht-radioaktiven Materialien, wie sie zur Erstellung einer Dokumentation erforderlich sind, fällt nicht in diese Begriffsbestimmung nach § 4 StrlSchG."

  - id: m1-quiz2
    type: mcq
    prompt: "Auf welchen Grundlagen basiert der Strahlenschutz?"
    points: 1
    choices:
      - id: a1
        text: "Auf physikalischen Grundlagen"
        correct: true
        feedback: "Ihre Antwort ist korrekt."
      - id: a2
        text: "Auf empirisch gewonnen Erfahrungen"
        correct: false
        feedback: "Ihre Antwort ist falsch. Empirisch gewonnene Erfahrungen sind wertvoll, aber die Grundlagen basieren auf physikalischen Gesetzmäßigkeiten."
      - id: a3
        text: "Aus Recherche im Internet und Einsatz von KI"
        correct: false
        feedback: "Ihre Antwort ist falsch. Internetrecherche/KI können Hilfsmittel sein, ersetzen aber keine physikalischen Grundlagen."
```

#### Further reading

- [Strahlenschutzgesetz](https://www.gesetze-im-internet.de/strlschg/)

#### Common misconceptions

```yaml
- misconception:
  correction:

- misconception:
  correction:
```

#### Grade

```yaml
completion: # Completion rules for this module
  required: true # Module must be completed to finish course
  passing_percent: 70 # Module pass threshold (if you enforce per-module)
grade_items: # Items that show up in gradebook
  - id: m1-quiz # Grade item id (referenced in attempts)
    points_total: 2 # Total points across quiz items above
```

### Module 2: Atome und Atomkerne {#m2}

#### Content

##### Bohrsches Atommodell

Das Bohrsche Atommodell wurde 1913 von Niels Bohr entwickelt. Es war das erste Atommodell mit Elementen der (damals noch nicht entwickelten) Quantenmechanik, das weite Anerkennung fand.

Atome bestehen im Bohrschen Atommodell aus einem schweren, positiv geladenen Atomkern und leichten, negativ geladenen Elektronen, die den Atomkern auf geschlossenen Bahnen umkreisen.

Der Durchmesser eines Atomkerns beträgt etwa $10^{-15}$ Meter oder 1 Femtometer (fm).

Ein Femtometer (fm) ist eine Längeneinheit im Internationalen Einheitensystem, die $10^{-15}$ Metern entspricht, also einem Billiardstel Meter. Es wird oft als "Fermi" bezeichnet und ist in der Kernphysik die gebräuchliche Maßeinheit für den Durchmesser von Atomkernen.

Zum Vergleich: der Durchmesser eines menschlichen Haares ist etwa eine Milliarde ($10^9$) mal größer als der Durchmesser eines Atomkerns.

Der Atomkern besteht aus positiv geladenen Protonen und Neutronen. Die Neutronen sind neutral, d. h. sie tragen keine Ladung.

Protonen und Neutronen werden als Nukleonen bezeichnet.
Nukleonen sind die Bausteine des Atomkerns.
Die Gesamtzahl der Nukleonen in einem Atom wird als Massenzahl bezeichnet und bestimmt weitgehend die Masse des Atoms. Die Nukleonen werden durch die starke Kernkraft zusammengehalten, einer kurzreichweitigen, aber sehr starken Wechselwirkung.

Der Durchmesser der Atomhülle liegt im Bereich von $10^{-10}$ m. Diese Größe wird auch mit 1 &#8491 abgekürzt. Die Größe des Durchmessers wird durch die Elektronen auf den äußeren Bahnen bestimmt, wobei Atome keine scharfe Grenze haben, sondern die Elektronen einen Wahrscheinlichkeitsraum bilden.
Der Durchmesser der Atomhülle ist über 10000-mal größer als der Durchmesser des Atomkerns.

Für die Beschreibung der Bewegung der Elektronen setzte Bohr durch drei Postulate die klassische Physik teilweise außer Kraft. Als Ergebnis gibt das Bohrsche Atommodell, anders als ältere Atommodelle, viele der am Wasserstoffatom beobachteten Eigenschaften richtig wieder. Andererseits werden viele Details sehr genauer spektroskopischer Messungen von dem Bohrschen Atommodell noch nicht erfasst und manche wichtige Eigenschaften gar nicht erklärt, darunter die räumliche Gestalt und die Möglichkeit zur chemischen Bindung.

Ein Atom mit der gleichen Anzahl an positiv geladenen Protonen und negativ geladenen Elektronen ist elektrisch neutral.

Ist die Anzahl an Protonen eines Atoms ungleich der Anzahl an Elektronen wird es als Ion bezeichnet. Ist die Anzahl an Protonen größer als die Anzahl an Elektronen wird das Atom als positiv geladenes Atom bezeichnet.
Ist die Anzahl an Protonen kleiner als die Anzahl an Elektronen wird das Atom als negativ geladenes Atom bezeichnet.

##### Atome und chemische Elemente

Atome sind die Grundbausteine der chemischen Elemente.
Das chemische Verhalten der Atome wird durch die Zahl der Protonen im Kern und durch den daraus resultierenden Aufbau der Elektronenhülle bestimmt.

###### Beispiele chemischer Elemente

Wasserstoff (H) besteht aus einem Proton im Kern und einem Elektron in der Hülle.
Helium (He) besteht aus zwei Protonen im Kern und zwei Elektronen in der Hülle.
Sauerstoff (O) besteht aus acht Protonen im Kern und acht Elektronen in der Hülle.
Uran (U) besteht aus 92 Protonen im Kern und 92 Elektronen in der Hülle.

##### Nuklide und Isotope

Ein Nuklid ist irgendeine Kombination von Protonen und Neutronen, die einen Atomkern bilden.
Ein Nuklid wird durch die Zahl seiner Protonen (Ordnungszahl) und die Summe der Zahl seiner Protonen und Neutronen (Massenzahl) beschrieben. Die Schreibweise hierfür ist $_{A}^{M}X$. X ist ein Platzhalter für das chemische Symbol (z. B. H, He, O, U).

Es sind mehr als 2000 verschiedene Nuklide bekannt. Die meisten dieser Nuklide sind radioaktiv.

Nuklide mit gleicher Ordnungszahl, aber unterschiedlicher Massenzahl heißen Isotope.

###### Beispiele von Isotopen

Wasserstoff-Isotope: $_{1}^{1}H$, $_{1}^{2}H$, $_{1}^{3}H$

Kohlenstoff-Isotope: $_{6}^{12}C$, $_{6}^{14}C$

Uran-Isotope: $_{92}^{235}U$, $_{92}^{238}U$

##### Nuklidkarte

Alle Nuklide lassen sich in einer Nuklidkarte in Segrè-Darstellung schematisch darstellen. Eine oftmals genutzte Darstellung besteht aus einem kartesischen Z,N-Koordinatensystem. Auf der waagerechten Achse ist die Zahl an Protonen Z und auf der vertikalen Achse die Zahl an Neutronen N aufgetragen.
Die bekannten Radinuklide befinden sich entlang der Diagonalen der Z,N-Ebene.

On-line Versionen der Nuklidkarte sind verfügbar unter:

- Online-Nuklidkarte des Brookhaven National Laboratory mit vielen Details und Export-Funktion (englisch) [https://www.nndc.bnl.gov/nudat3/](https://www.nndc.bnl.gov/nudat3/)

- Online-Nuklidkarte der Internationalen Atomenergie-Organisation (englisch) [https://www-nds.iaea.org/relnsd/vcharthtml/VChartHTML.html](https://www-nds.iaea.org/relnsd/vcharthtml/VChartHTML.html)

#### Questions (practice / free-response)

```yaml
- id: m2-q1
  prompt: "In welcher Beziehung unterscheiden sich Isotope eines Elements voneinander?"
  reference_answer: "Isotope eines Elements haben eine unterschiedliche Anzahl an Neutronen."
  points: 1

- id: m2-q2
  prompt: "Beschreiben Sie in kurzen Sätzen das Bohrsche Atommodell."
  reference_answer: "Das Bohrsche Atommodell besteht aus einem Atomkern und einer ihn umgebenden Atomhülle. Der Atomkern setzt sich aus positiv geladenen Protonen und elektrisch neutralen Neutronen zusammen. Die Atomhülle enthält Elektronen, die sich auf geschlossenen Bahnen um den Atomkern bewegen."
  points: 1

- id: m2-q3
  prompt: "Wodurch werden die chemischen Eigenschaften eines Atoms festgelegt?"
  reference_answer: "Das chemische Verhalten der Atome wird durch die Anzahl der Protonen im Atomkern und durch den daraus resultierenden Aufbau der Elektronenhülle bestimmt."
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
    prompt: "Was sind Nukleonen? (wählen Sie bitte eine Antwort aus)"
    points: 1
    choices:
      - id: a1
        text: "Nukleonen sind die einen Atomkern bildenden Protonen und Neutronen."
        correct: true
        feedback: "Ihre Antwort ist korrekt."
      - id: a2
        text: "Nukleonen bezeichnen ein chemisches Element (z. B. Sauerstoff oder Stickstoff)."
        correct: false
        feedback: "Ihre Antwort ist nicht richtig! Ein chemisches Element ist ein Grundstoff, der aus nur einer einzigen Atomart besteht, erkennbar an der gleichen Anzahl von Protonen (Ordnungszahl) in jedem seiner Atome, Neutronen und Elektronen."
      - id: a3
        text: "Die Instandsetzung einer Röntgeneinrichtung."
        correct: false
        feedback: "Ihre Antwort ist völlig falsch! Lesen Sie sich den Abschnitt Atome und Atomkerne nochmals genauer durch."

  - id: m2-quiz2
    type: mcq
    prompt: "Woraus besteht ein Atomkern? (wählen Sie bitte eine Antwort aus)"
    points: 1
    choices:
      - id: a1
        text: "Aus Nukleonen, den Protonen und Neutronen."
        correct: true
        feedback: "Ihre Antwort ist korrekt."
      - id: a2
        text: "Aus Elektronen."
        correct: false
        feedback: "Ihre Antwort ist falsch. Elektronen befinden sich in der Atomhülle und nicht im Atomkern."
      - id: a3
        text: "Aus Protonen und Elektronen."
        correct: false
        feedback: "Ihre Antwort ist falsch! Protonen befinden sich zwar im Atomkern, Elektronen aber in der Atomhülle."

  - id: m2-quiz3
    type: mcq
    prompt: "Durch was wird das chemische Verhalten eines Atoms bestimmt? (wählen Sie bitte eine Antwort aus)"
    points: 1
    choices:
      - id: a1
        text: "Durch die Zahl der Protonen im Kern und dem daraus resultierenden Aufbau der Elektronenhülle."
        correct: true
        feedback: "Ihre Antwort ist korrekt."
      - id: a2
        text: "Durch die Zahl der Neutronen im Kern."
        correct: false
        feedback: "Ihre Antwort ist falsch. Die Anzahl der ungeladenen Neutronen hat keinen Einfluss auf das chemische Verhalten der Atome."
      - id: a3
        text: "Durch die Zahl der Elektronen im Kern."
        correct: false
        feedback: "Ihre Antwort ist falsch. Elektronen befinden sich in der Atomhülle und nicht im Atomkern."
      - id: a4
        text: "Durch die Zahl der Protonen."
        correct: false
        feedback: "Ihre Antwort ist fast richtig, damit aber trotzdem falsch! Protonen befinden sich zwar im Atomkern und bestimmen mit das chemische Verhalten. Allerdings wird dieses zusätzlich auch von den Elektronen in der Atomhülle mit beeinflusst."

  - id: m2-quiz4
    type: mcq
    prompt: "Worin unterscheiden sich die Isotope eines Elements? (wählen Sie bitte eine Antwort aus)"
    points: 1
    choices:
      - id: a1
        text: "Durch ihre Massenzahl."
        correct: true
        feedback: "Ihre Antwort ist korrekt."
      - id: a2
        text: "Durch ihre Ordnungszahl."
        correct: false
        feedback: "Ihre Antwort ist falsch. Die Ordnungszahl gibt die Anzahl an Protonen wieder und legt damit das Element fest."
      - id: a3
        text: "Durch die Zahl der Elektronen in der Atomhülle."
        correct: false
        feedback: "Ihre Antwort ist falsch. Die Zahl der Elektronen ist für alle Isotope eines Elements gleich."
      - id: a4
        text: "Durch die Summe der Protonen und Elektronen."
        correct: false
        feedback: "Ihre Antwort ist falsch."
```

#### Further reading

- [Strahlenschutzgesetz](https://www.gesetze-im-internet.de/strlschg/)

#### Common misconceptions

```yaml
- misconception:
  correction:

- misconception:
  correction:
```

#### Grade

```yaml
completion:
  required: true
  passing_percent: 70
grade_items:
  - id: m2-quiz
    points_total: 4
```

### Module 3: Strahlung {#m3}

#### Content

##### Was ist Strahlung

Strahlung beschreibt die Ausbreitung von Teilchen und Wellen, deren gemeinsames Merkmal der **Transport von Energie** ist. Im Falle von Teilchen erfolgt der Energietransport durch die sogenannte Korpuskularstrahlung, im Falle von elektromagnetischen Wellen durch Wellenstrahlung.

Jegliche Strahlung hat

- eine **Ursache**, d. h. eine Strahlenquelle, und
- eine **Richtung**, die Strahlungsrichtung.

Beispiele für Strahlenquellen sind

- radioaktive Stoffe (Gamma-Strahlung, Röntgen-Strahlung),
- Mobilfunk (Mikrowellen-Strahlung) oder
- Lampen (Licht)

Trifft Strahlung auf ein Material - egal, ob fest, flüssig oder gasförmig - d. h. auf Materie die aus Atomen oder Molekülen aufgebaut ist, dann kann sie mit dieser in **Wechselwirkung** treten. Die Wechselwirkungen können beispielsweise in Form von

- Absorption oder
- Streuung

stattfinden.

Bei der **Absorption** wird die Energie der Strahlung vom Material, in das die Strahlung eindringt, aufgenommen. Bei der **Streuung** wird die Richtung der Strahlung geändert und zusätzlich kann ein Teil ihrer Energie vom Material aufgenommen werden.

Unter **Transmission** versteht man den Durchgang der Strahlung durch Materie, bei der die Richtung der Strahlung nicht geändert wird. Es kann aber ein Teil der Strahlungsenergie auf dem Weg durch die Materie absorbiert und/oder gestreut werden, d. h. die Energie und/oder die „Menge“ an Strahlung nach dem Durchgang durch das Material können geringer sein als vor Eintritt in das Material.

##### Was ist ionisierende Strahlung

Als ionisierende Strahlung wird jede Teilchen- oder elektromagnetische Strahlung bezeichnet, die durch Wechselwirkung mit Atomen oder Molekülen aus diesen Elektronen freisetzen oder chemische Bindungen aufbrechen kann, sodass positiv geladene Ionen oder Molekülreste zurückbleiben. Dieser Vorgang wird als **Ionisation** bezeichnet. Hierfür sind Energien von mehr als 5 eV (Elektronen-Volt) erforderlich. Für die im menschlichen Körper vorkommenden chemischen Elemente beträgt die minimale Ionisierungsenergie ca. 20 eV.

Man unterscheidet zwischen **direkt ionisierender** und **indirekt ionisierender Strahlung**. Im Falle direkt ionisierender Strahlung geben geladene Teilchen (z. B. Elektronen, Protonen, α-Teilchen, β-Teilchen) beim Durchgang durch Materie aufgrund ihrer elektrischen Ladung Anregungs- und Ionisationsenergie an die Atome oder Moleküle ab und können diese hierdurch ionisieren.

Ungeladene Strahlung, wie die elektromagnetische Strahlung oder ungeladene Teilchen, können die Atome oder Moleküle über die Erzeugung eines geladenen Sekundärteilchens ionisieren. Im Falle von Gamma- oder Röntgen-Strahlung (elektromagnetische Strahlung) können dies Sekundärelektronen sein, bei ungeladenen Teilchen, wie beispielsweise Neutronen, Rückstreuprotonen.

##### Die Energieeinheit Elektronenvolt

Energie ist eine physikalische Größe. Ihre praktische Bedeutung liegt oft darin, dass ein physikalisches System in dem Maß Wärme abgeben, Arbeit leisten oder Strahlung aussenden kann, in dem sich seine Energie verringert. Die Energie wird hierbei in **Joule (J)** angegeben.

Im Zusammenhang mit ionisierender Strahlung erfolgt die Energieangabe unter Verwendung einer speziellen Einheit, dem **Elektronenvolt (eV)**.

Der Zusammenhang zwischen den Einheiten Joule und dem Elektronenvolt ist durch die Beziehung

$1~eV = 1,6\cdot 10^{-19}~J$

gegeben. Ein Elektronenvolt beschreibt folglich sehr kleine Energien im Vergleich zu einem Joule.

Ein Joule ist die Energie, die benötigt wird, um beispielsweise einen Körper mit einer Masse von ca. 102 Gramm um einen Meter anzuheben (Anmerkung: hierfür wird eine Kraft von einem Newton benötigt).

Die Größe $1~eV$ lässt sich auch anschaulich beschreiben: Sie ist die Energie der Bewegung (**Bewegungsenergie**), die ein Elektron erhält, wenn es im Vakuum eine Spannungsdifferenz von $U=1~eV$ durchlaufen hat.

Wie wir gleich sehen werden, decken die verschiedenen Strahlungen einen sehr großen Energiebereich ab. Da man bei der Angabe von Energiewerten Zahlen mit zu vielen Stellen vermeiden will, hat sich die Verwendung von sogenannten Vorsätzen für Maßeinheiten als extrem praktisch erwiesen. Hierbei wird ein Buchstabe (der sog. **Präfix**) der Einheit eV vorangestellt. In unserem täglichen Umfeld verwenden wir diese Präfixe bereits wie selbstverständlich, beispielsweise für die Angabe von Massen. So sagen wir anstelle von $1000~g$ meistens $1~kg$. Hierbei wurde das Präfix k vor die Bezeichnung für die Einheit Gramm (_g_) geschrieben. _k_ bedeutet, dass der angegebene Wert in der Basiseinheit (hier g\*) tausend Mal größer ist als der Zahlenwert.

Einige der im Zusammenhang mit Strahlung am häufigsten verwendete Vorsätze sind nachfolgend aufgeführt:

| Präfix | Name  | Wert (Zahl)         | Wert (Potenz) | Wert (Wort) |
| ------ | ----- | ------------------- | ------------- | ----------- |
| µ      | Mikro | 0,000001            | $10^{-6}$     | Millionstel |
| m      | Milli | 0,001               | $10^{-3}$     | Tausendstel |
| k      | Kilo  | 1000                | $10^3$        | Tausend     |
| M      | Mega  | 1000000             | $10^6$        | Million     |
| G      | Giga  | 1000000000          | $10^9$        | Milliarde   |
| T      | Terra | 1000000000000       | $10^{12}$     | Billion     |
| P      | Peta  | 1000000000000000    | $10^{15}$     | Billiarde   |
| E      | Exa   | 1000000000000000000 | $10^{18}$     | Trillion    |

###### Beispiele für Energiebereiche der verschiedenen Strahlungsarten

Mit dem Wissen der Bedeutung der **Präfixe** lassen sich die in nachfolgender Auflistung angeführten typischen Energiebereiche für die verschiedenen Strahlungsarten besser verstehen.

| Strahlungsart              | Energiebereich                 |
| -------------------------- | ------------------------------ |
| Röntgen-Strahlung          | ~$10~keV$ bis $300~keV$        |
| Gamma-Strahlung            | ~$100~keV$ bis $3~MeV$         |
| Alpha-Strahlung            | ~$3~MeV$ bis $10~MeV$          |
| medizinische Beschleuniger | bis zu $25~meV$                |
| kosmische Strahlung        | bis zu $10^{14}~MeV = 100~EeV$ |

##### Ionisierende Strahlung und andere Strahlenarten

Eine graphische Darstellung der verschiedenen Bereiche des elektromagnetischen Spektrums zeigt [https://de.wikipedia.org/wiki/Elektromagnetisches_Spektrum#/media/Datei:Electromagnetic_spectrum_-de_c.svg(https://de.wikipedia.org/wiki/Elektromagnetisches_Spektrum#/media/Datei:Electromagnetic_spectrum_-de_c.svg)]. Die typischen Eingruppierungen der verschiedenen Strahlungsbereiche mit ihren zugehörigen Bezeichnungen sind dort entsprechend ihrer Wellenlängen und Frequenzen dargestellt.

Die „Größe“ einer elektromagnetischen Strahlung kann als Energie (Einheit eV), Wellenlänge (Einheit m) oder Frequenz (Einheit Hz) angegeben werden, da diese Größen über Formeln direkt miteinander in Beziehung stehen, d. h. ein in Elektronenvolt angegebener Wert kann in den entsprechenden Wert in Meter oder in Herz umgerechnet werden oder umgekehrt. Ein entsprechender online-Rechner findet sich beispielsweise unter [https://rechneronline.de/spektrum/(https://rechneronline.de/spektrum/)].

Hier eine kleine Übersicht der zusammengehörigen Energie, Wellenlängen und Frequenzwerte, die mit dem online-Rechner bestimmt wurden

| Energie | Frequenz   | Wellenlänge |
| ------- | ---------- | ----------- |
| 1 eV    | 241,79 THz | 1,2 µm      |
| 20 eV   | 4,8 PHz    | 62 nm       |
| 1 keV   | 241,8 PHz  | 1,2 nm      |
| 1 MeV   | 241,8 EHz  | 1,2 pm      |

Die für den Strahlenschutz relevanten Energien beginnen bei ca. 20 eV. Hier sei in diesem Zusammenhang nochmals darin erinnert, dass die minimale Ionisierungsenergie für im menschlichen Körper vorkommenden chemischen Elemente ca. 20 eV beträgt.

Aus der Abbildung kann man auch entnehmen, dass sichtbares Licht, Infrarot-, Terraherz-, Mikrowellen- und Rundfunk-Strahlung sowie Wechselströme nicht zu einer Ionisation im menschlichen Körper führen können, da ihre Energien unter einem Elektronenvolt liegen und damit zu niedrig sind.

##### Wichtige Arten ionisierender Strahlung

Im praktischen Strahlenschutz sind im Wesentlichen vier Strahlungsarten zu berücksichtigen.

- die elektrisch geladenen **Alpha-** und **Beta-Teilchen** sowie
- die elektrisch neutralen **Photonen** und **Neutronen**.

Deren wichtigsten Eigenschaften sind nachfolgend kurz zusammengefasst.

###### Alpha-Teilchen ($\alpha$-Teilchen)

Ein Alpha-Teilchen besteht aus 2 Protonen und 2 Neutronen und hat keine Elektronen. Damit ist es zweifach positiv geladen.

###### Beta-Teilchen ($\beta$-Teilchen)

Beta-Teilchen können in zwei Versionen vorkommen. Zum einen als **Elektronen**, die eine negative Elementarladung besitzen, zum anderen als **Positronen**, die eine positive Elementarladung besitzen.

Elektronen und Positronen sind fast identisch. Sie unterscheiden sich nur hinsichtlich ihrer Ladung, die für Elektronen negativ, für Positronen positiv ist.

Das Positron wird auch als Antiteilchen des Elektrons bezeichnet. Treffen ein Elektron und ein Positron aufeinander, dann vernichten sie sich (die sogenannte Annihilation) und wandeln ihre Masse vollständig in Strahlung um.

###### Photonen

Photonen könne in Form von **Röntgen-** oder **Gamma-Strahlung** auftreten.

Röntgenstrahlung hat ihren Ursprung in der Elektronenhülle eines Nuklids, Gamma-Strahlung im Atomkern.

Bei Photonen handelt es sich um elektromagnetische Strahlung, die keine Ladung hat und auch keine (Ruhe-)Masse.

###### Neutronen

Neutronen sind Bestandteile des Kerns und können beispielsweise bei der Kernspaltung freigesetzt werden. Ein Neutron ist etwa 1839-mal schwerer als ein Elektron und hat keine elektrische Ladung.

##### Reichweiten ionisierender Strahlung

Aus Sicht des aktiven Strahlenschutzes ist es wichtig die **Reichweiten** der verschiedenen Strahlungsarten in Luft zu kennen. Damit kann bereits eine erste Abschätzung getroffen werden, ob Strahlenschutzmaßnahmen überhaupt erforderlich sind und wenn ja, welche. Wäre beispielsweise die Reichweite der Strahlung aus einer Strahlenquelle nur wenige Millimeter, die kleinste Entfernung, die eine Person zu dieser Strahlenquelle unter allen denkbaren Umständen einnehmen kann, aber im Bereich von Metern, dann könnte auf Strahlenschutzmaßnahmen verzichtet werden.

Betrachten wir nun die vier zuvor behandelten Strahlungsarten hinsichtlich ihrer typischen Reichweiten. Zu berücksichtigen ist, dass diese von der Energie der Strahlung abhängt. Je höher die Energie, desto weitreichender ist die Strahlung.

| Alpha-Strahlung      |                         |
| -------------------- | ----------------------- |
| Reichweite in Luft   | wenige Zentimeter (~cm) |
| Reichweite in Gewebe | einige Mikrometer (~µm) |

| Beta-Strahlung       |                           |
| -------------------- | ------------------------- |
| Reichweite in Luft   | maximal wenige Meter (~m) |
| Reichweite in Gewebe | wenige Millimeter (~mm)   |

| Photonen             |                 |
| -------------------- | --------------- |
| Reichweite in Luft   | viele Meter (m) |
| Reichweite in Gewebe | viele Meter (m) |

| Neutronen            |                                                                          |
| -------------------- | ------------------------------------------------------------------------ |
| Reichweite in Luft   | nahezu unbeschränkt (viele Meter)                                        |
| Reichweite in Gewebe | zum Teil sehr große Reichweite (hängt stark von der Neutronenenergie ab) |

##### Strahlungsenergie und Strahlungsintensität

Zwei weitere relevante Größen im praktischen Strahlenschutz sind die Begriffe der **Strahlungsenergie** und der **Strahlungsintensität**.

Unter dem Begriff **Strahlungsenergie** versteht man die Energie, die die Strahlung, d. h. ein Teilchen, ein Photon oder ein Neutron, besitzt. Die Art und Stärke der Wechselwirkung der Strahlung mit Materie wird unter anderem von der Größe der Energie bestimmt.

Strahlungsenergien, die zum Beispiel beim radioaktiven Zerfall auftreten, sind die charakteristischen Energien der emittierten Gamma-Strahlung oder Teilchen. Einige Beispiele hierfür sind nachfolgend aufgeführt:

| Gamma-Strahlung |               |
| --------------- | ------------- | ------------ |
| $^{241}Am$      | Americium-241 | $59,5~keV$   |
| $^{137}Cs$      | Cäsium-137    | $661,7~keV$  |
| $^{60}Co$       | Cobalt-60     | $1173,2~keV$ |
| $^{60}Co$       | Cobalt-60     | $1332,5~keV$ |

_Beachte: radioaktive Isotope können Gamma-Strahlung mit verschiedenen charakteristischen Strahlungsenergien aussenden (siehe $^{60}Co$_).

| Alpha-Strahlung |             |             |
| --------------- | ----------- | ----------- |
| $^{226}Ra$      | Radium-226  | $4,78~MeV$  |
| $^{232}Th$      | Thorium-232 | $4,01~MeV$  |
| $^{228}Th$      | Thorium-228 | $5,42~MeV$  |
| $^{235}U$       | Uran-235    | $4,392~MeV$ |

Doch nicht nur die Strahlungsenergie spielt eine Rolle, sondern auch deren „Menge“. Diese wird durch den Begriff der **Strahlungsintensität** festgelegt.

Die **Strahlungsintensität** bezeichnet die Anzahl an Teilchen, Photonen oder Neutronen, die eine bestimmte Fläche innerhalb eines bestimmten Zeitintervalls durchdringen. Für eine bessere Vergleichbarkeit verschiedener Werte bezieht man die Fläche auf eine Einheitsfläche, oftmals $1~cm^2$ oder $1~m^2$. Das Zeitintervall wird oftmals auf 1 s bezogen. Hieraus ergibt sich für die Einheit der Strahlungsintensität $cm^{-2} \cdot s^{-1}$ oder $m^{-2}·s^{-1}$. Aus dieser Einheit leitet sich auch die alternative Bezeichnung **Teilchenflussdichte** ab.

Berücksichtigt man in der Strahlungsintensität auch die pro Flächen- und Zeiteinhalt transportierte Energie, so spricht man von **Energieflussdichte**. Die Einheit ist dann $eV \cdot cm^{-2} \cdot s^{-1}$ oder $eV \cdot m^{-2} \cdot s^{-1}$, d. h. Energie pro Fläche und pro Zeiteinheit.

#### Questions (practice / free-response)

```yaml
- id: m3-q1
  prompt: "Was versteht man unter Transmission von Strahlung?"
  reference_answer: "Unter Transmission von Strahlung versteht man den Durchgang der Strahlung durch Materie, bei der die Richtung der Strahlung nicht geändert wird. Es kann aber ein Teil der Strahlungsenergie auf dem Weg durch die Materie absorbiert und/oder gestreut werden, d. h. die Energie und/oder die „Menge“ an Strahlung nach dem Durchgang durch das Material könne geringer sein als vor Eintritt in das Material."
  points: 1

- id: m3-q2
  prompt: "Was ist ionisierende Strahlung?"
  reference_answer: "Als ionisierende Strahlung wird jede Teilchen- oder elektromagnetische Strahlung bezeichnet, die durch Wechselwirkung mit Atomen oder Molekülen aus diesen Elektronen freisetzen oder chemische Bindungen aufbrechen kann, sodass positiv geladene Ionen oder Molekülreste zurückbleiben. Dieser Vorgang wird als Ionisation bezeichnet. Hierfür sind Energien von mehr als 5 eV (Elektronen-Volt) erforderlich. Für die im menschlichen Körper vorkommenden chemischen Elemente beträgt die minimale Ionisierungsenergie ca. 20 eV."
  points: 1

- id: m3-q3
  prompt: "Wie unterscheidet sich direkt ionisierende und indirekt ionisierende Strahlung?"
  reference_answer: "Im Falle direkt ionisierender Strahlung geben geladene Teilchen (z. B. Elektronen, Protonen, α-Teilchen, β-Teilchen) beim Durchgang durch Materie aufgrund ihrer elektrischen Ladung Anregungs- und Ionisationsenergie an die Atome oder Moleküle ab und können diese hierdurch ionisieren. Ungeladene Strahlung, wie die elektromagnetische Strahlung oder ungeladene Teilchen, können die Atome oder Moleküle über die Erzeugung eines geladenen Sekundärteilchens ionisieren. Im Falle von Gamma- oder Röntgen-Strahlung (elektromagnetische Strahlung) können dies Sekundärelektronen sein, bei ungeladenen Teilchen, wie beispielsweise Neutronen, Rückstreuprotonen."
  points: 1

- id: m3-q4
  prompt: "Nennen Sie Beispiele für ionisierende Strahlung."
  reference_answer: "Beispiele für ionisierende Strahlung haben alle unterschiedliche Ursachen (d. h. Strahlungsquellen), jedoch die gleiche Wirkung auf Materie. Hierzu gehören Röntgen-Strahlung, Gamma-Strahlung, Kern-Strahlung (Radioaktivität), Strahlung aus Beschleunigern, kosmische Strahlung, Neutronen."
  points: 1

- id: m3-q5
  prompt: "Beschreiben Sie die praktische Bedeutung der Energieeinheit Elektronenvolt."
  reference_answer: "Die praktische Bedeutung der Energieeinheit Elektronenvolt liegt oft darin, dass ein physikalisches System in dem Maß Wärme abgeben, Arbeit leisten oder Strahlung aussenden kann, in dem sich seine Energie verringert."
  points: 1

- id: m3-q6
  prompt: "Beschreiben Sie die Größe 1 eV anschaulich."
  reference_answer: "Sie ist die Energie der Bewegung (Bewegungsenergie), die ein Elektron erhält, wenn es im Vakuum eine Spannungsdifferenz von U = 1 eV durchlaufen hat."
  points: 1

- id: m3-q7
  prompt: "Nennen Sie wichtige Arten ionisierender Strahlung, die für den praktischen Strahlenschutz relevant sind."
  reference_answer: "Im praktischen Strahlenschutz werden im Wesentlichen vier Strahlungsarten berücksichtigt. Die elektrisch geladenen Alpha- und Beta-Teilchen sowie die elektrisch neutralen Photonen und Neutronen."
  points: 1

- id: m3-q8
  prompt: "Was versteht man unter dem Begriff Strahlungsenergie?"
  reference_answer: "Unter dem Begriff Strahlungsenergie versteht man die Energie, die die Strahlung, d. h. ein Teilchen, ein Photon oder ein Neutron, besitzt. Die Art und Stärke der Wechselwirkung der Strahlung mit Materie wird unter anderem von der Größe der Energie bestimmt."
  points: 1

- id: m3-q9
  prompt: "Was versteht man unter dem Begriff Strahlungsintensität?"
  reference_answer: "Die Strahlungsintensität bezeichnet die Anzahl an Teilchen, Photonen oder Neutronen, die eine bestimmte Fläche innerhalb eines bestimmten Zeitintervalls durchdringen."
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
    prompt: "Was hat jegliche Strahlung? (wählen Sie bitte eine Antwort aus)"
    points: 1
    choices:
      - id: a1
        text: "Eine Ursache und eine Richtung."
        correct: true
        feedback: "Ihre Antwort ist korrekt."
      - id: a2
        text: "Eine Farbe."
        correct: false
        feedback: 'Ihre Antwort ist nicht richtig. Lesen Sie den Abschnitt "Was ist Strahlung?" nochmals genau durch.'
      - id: a3
        text: "Eine Wirkung."
        correct: false
        feedback: "Ihre Antwort ist nicht vollständig. Es fehlt noch etwas."

  - id: m3-quiz2
    type: mcq
    prompt: "Was ist ionisierende Strahlung? (wählen Sie bitte eine Antwort aus)"
    points: 1
    choices:
      - id: a1
        text: "Ionisierende Strahlung kann eine Teilchen-Strahlung oder eine elektromagnetische Strahlung sein, die durch Wechselwirkung mit Atomen aus diesen Elektronen freisetzen."
        correct: true
        feedback: "Ihre Antwort ist korrekt."
      - id: a2
        text: "Ionisierende Strahlung kann eine Teilchen-Strahlung oder eine elektromagnetische Strahlung sein, die durch Wechselwirkung mit Atomkernen Protonen freisetzt."
        correct: false
        feedback: "Ihre Antwort ist falsch! Teilchen- oder elektromagnetische Strahlung, wie wir sie hier betrachte, setzen durch Wechselwirkung keine Protonen aus dem Atomkern frei."
      - id: a3
        text: "Ionisierende Strahlung kann eine Teilchen-Strahlung oder eine elektromagnetische Strahlung sein, die durch Wechselwirkung mit Atomkernen Neutronen freisetzen."
        correct: false
        feedback: "Ihre Antwort ist falsch! Teilchen- oder elektromagnetische Strahlung, wie wir sie hier betrachte, setzen durch Wechselwirkung keine Neutronen aus dem Atomkern frei."

  - id: m3-quiz3
    type: mcq
    prompt: "Welche Strahlungen werden der Gruppe der direkt ionisierenden Strahlungen zugeordnet? (wählen Sie bitte eine Antwort aus)"
    points: 1
    choices:
      - id: a1
        text: "α- und β-Strahlung"
        correct: true
        feedback: "Ihre Antwort ist korrekt."
      - id: a2
        text: "α-, β- und Neutronen-Strahlung"
        correct: false
        feedback: "Ihre Antwort ist falsch. Warum kann Neutronen-Strahlung nicht direkt ionisierend wirken"
      - id: a3
        text: "Röntgen- und Gamma-Strahlung sowie sichtbares Licht"
        correct: false
        feedback: "Ihre Antwort ist falsch. Keine der von Ihnen genannten Strahlungsarten ist elektrisch geladen."
      - id: a4
        text: "Gamma- und Neutronen-Strahlung"
        correct: false
        feedback: "Ihre Antwort ist falsch. Keine der von Ihnen genannten Strahlungsarten ist elektrisch geladen."
      - id: a5
        text: "Keine! Es gibt nur indirekt ionisierende Strahlung."
        correct: false
        feedback: "Ihre Antwort ist falsch. Lesen Sie sich bitte den entsprechenden Abschnitt nochmals genau durch."

  - id: m3-quiz4
    type: mcq
    prompt: "Welche Energieeinheit wird für die Energie von Strahlung verwendet? (wählen Sie bitte eine Antwort aus)"
    points: 1
    choices:
      - id: a1
        text: "Elektronenvolt (eV)"
        correct: true
        feedback: "Ihre Antwort ist korrekt."
      - id: a2
        text: "W (Watt)"
        correct: false
        feedback: "Ihre Antwort ist falsch. Watt ist die Einheit der Leistung."
      - id: a3
        text: "N (Newton)"
        correct: false
        feedback: "Ihre Antwort ist falsch. Newton ist die Einheit der Kraft."
      - id: a4
        text: "A (Ampere)"
        correct: false
        feedback: "Ihre Antwort ist falsch. Ampere ist die Einheit der Stromstärke."
      - id: a5
        text: "V (Volt)"
        correct: false
        feedback: "Ihre Antwort ist falsch. Volt ist die Einheit der Spannung."

  - id: m3-quiz5
    type: mcq
    prompt: "Wie hoch kann eine Tafel Schokolade (ca. 100 g) mit der Energie von 1 eV ungefähr angehoben werden? (wählen Sie bitte eine Antwort aus)"
    points: 1
    choices:
      - id: a1
        text: "1 m"
        correct: true
        feedback: "Ihre Antwort ist korrekt."
      - id: a2
        text: "50 cm"
        correct: false
        feedback: "Ihre Antwort ist falsch!"
      - id: a3
        text: "3,2 mm"
        correct: false
        feedback: "Ihre Antwort ist falsch!"
      - id: a4
        text: "1,8 m"
        correct: false
        feedback: "Ihre Antwort ist falsch!"
      - id: a5
        text: "9 µm"
        correct: false
        feedback: "Ihre Antwort ist falsch."

  - id: m3-quiz6
    type: mcq
    prompt: "Welche Strahlungsarten sind elektrisch geladen? (wählen Sie bitte eine Antwort aus)"
    points: 1
    choices:
      - id: a1
        text: "Alpha-Teilchen, Beta-Teilchen, Photonen und Neutronen"
        correct: false
        feedback: "Ihre Antwort ist falsch."
      - id: a2
        text: "Alpha-Teilchen, Photonen und Neutronen"
        correct: false
        feedback: "Ihre Antwort ist falsch!"
      - id: a3
        text: "Photonen, Neutronen"
        correct: false
        feedback: "Ihre Antwort ist falsch!"
      - id: a4
        text: "Alpha-Teilchen und Beta-Teilchen"
        correct: true
        feedback: "Ihre Antwort ist richtig!"

  - id: m3-quiz7
    type: mcq
    prompt: "Wie groß ist die typische Reichweite der verschiedenen Strahlungsarten in Gewebe? (wählen Sie bitte eine Antwort aus)"
    points: 1
    choices:
      - id: a1
        text: "Die Reichweite in Gewebe beträgt für Alpha-Teilchen einige µm, für Beta-Teilchen wenige mm und für Photonen viele Meter. Neutronen haben zum Teil eine sehr große Reichweite."
        correct: true
        feedback: "Ihre Antwort ist richtig."
      - id: a2
        text: "Die Reichweite in Gewebe beträgt für Alpha-Teilchen einige mm, für Beta-Teilchen wenige µm und für Photonen viele Meter. Neutronen haben zum Teil eine sehr große Reichweite."
        correct: false
        feedback: "Ihre Antwort ist falsch! Schauen Sie sich die Reichweiten für Alpha-Teilchen und für Beta-Teilchen nochmals genauer an."
      - id: a3
        text: "Die Reichweite in Gewebe beträgt für Alpha-Teilchen einige µm, für Beta-Teilchen wenige m und für Photonen einige cm. Neutronen haben zum Teil eine sehr große Reichweite."
        correct: false
        feedback: "Ihre Antwort ist falsch! Schauen Sie sich die Reichweiten für Beta-Teilchen und für Photonen nochmals genauer an."
      - id: a4
        text: "Die Reichweite in Gewebe beträgt für Alpha-Teilchen einige µm, für Beta-Teilchen wenige mm und für Photonen einige m. Neutronen werden an der Oberfläche des Gewebes reflektiert."
        correct: false
        feedback: "Ihre Antwort ist falsch! Schauen Sie sich die Reichweiten für Neutronen nochmals genauer an."
      - id: a5
        text: "Die Reichweite in Gewebe beträgt für Alpha-Teilchen einige cm, für Beta-Teilchen wenige µm und für Photonen einige mm. Neutronen haben zum Teil eine sehr kleine Reichweite."
        correct: false
        feedback: "Ihre Antwort ist falsch! Schauen Sie sich die Reichweiten aller Strahlungsarten nochmals genauer an."
```

#### Further reading

- Was ist ionisierende Strahlung: [https://www.fs-ev.org/fileadmin/user_upload/80_FAQs/strahlung_und_dosis/Frage_Nr_104.pdf](https://www.fs-ev.org/fileadmin/user_upload/80_FAQs/strahlung_und_dosis/Frage_Nr_104.pdf)
- Wie wirken sich ionisierende Strahlen auf den Menschen aus? [https://www.fs-ev.org/fileadmin/user_upload/80_FAQs/strahlung_und_dosis/Frage_Nr_102.pdf](https://www.fs-ev.org/fileadmin/user_upload/80_FAQs/strahlung_und_dosis/Frage_Nr_102.pdf)
- Was für natürliche Strahlung gibt es und wieviel? [https://www.fs-ev.org/fileadmin/user_upload/80_FAQs/strahlung_und_dosis/Frage_Nr_105.pdf](https://www.fs-ev.org/fileadmin/user_upload/80_FAQs/strahlung_und_dosis/Frage_Nr_105.pdf)

#### Common misconceptions

```yaml
- misconception:
  correction:

- misconception:
  correction:
```

#### Grade

```yaml
completion:
  required: true
  passing_percent: 70
grade_items:
  - id: m3-quiz
    points_total: 7
```

### Module 4: Wechselwirkung {#m4}

#### Content

##### Wechselwirkung ionisierender Strahlung mit Materie

Nachdem wir die Begriffe Atome, Atomkerne und Strahlung besprochen und gelernt haben, was unter Strahlungsenergie, Strahlungsintensität und Energieflussdichte verstanden wird, betrachten wir als nächstes etwas genauer, was passiert, wenn Strahlung auf Atome oder Atomkerne trifft, d. h. die Wechselwirkung von Strahlung mit Materie.

###### Was versteht man unter Wechselwirkung ionisierender Strahlung mit Materie?

Wie in den vorangegangenen Abschnitten beschrieben, wird durch α-, β- und γ-Strahlung sowie durch Neutronen Energie transportiert. Trifft nun Strahlung auf Materie, z. B. ein Gas, eine Flüssig-keit oder einen Festkörper, dann wird die Energie dieser Strahlung ganz oder teilweise auf die Materie übertragen. Dieser Übertrag kann durch Stöße (z. B. Ionisation, Anregung) oder Umwandlungsprozesse (z. B. Compton-Streuung, Photoeffekt, Paarbildung) stattfinden und wird allgemein als **Wechselwirkung der Strahlung mit Materie** bezeichnet.

Die gerade erwähnten Punkte werden wir im Folgenden näher betrachten.

**\*Zu beachten:** Die Wechselwirkung von Strahlung mit Materie (zu der natürlich auch der menschliche Körper zählt!) kann Veränderungen in der jeweiligen Materie verursachen, die unter Umständen zu Schädigungen führen können.\*

###### Aufbau von Materie

Beginnen wir mit der Beschreibung, was man unter Materie versteht. Materie besteht aus Atomen und Molekülen, die miteinander in Wechselwirkung stehen können. Abhängig von der Stärke dieser Wechselwirkung und der Mobilität der Atome und Moleküle unterscheidet man die drei verschiedenen Zustände

- fest
- flüssig oder
- gasförmig.

Diese drei Zustände der Materie bilden die klassischen **Aggregatzustände der Materie**. Als vierter Aggregatzustand wird Plasma bezeichnet, der aber hier nicht weiter betrachtet wird.

Auch wenn es aus uns der täglichen Erfahrung bereits klar ist, wollen wir uns zunächst die Abgrenzung der drei Aggregatszustände voneinander betrachten:

Im **festen Zustand** behält ein Material meist sowohl seine Form als auch sein Volumen bei. Der **flüssige Zustand** unterscheidet sich vom festen Zustand, dass seine Form sich den jeweiligen Gegebenheiten anpasst, das Volumen aber unverändert bleibt. Im **gasförmigen Zustand** entfällt auch noch die Volumenbeständigkeit, d. h. ein Gas füllt den zur Verfügung stehenden Raum vollständig aus.

Die Gründe für dieses Verhalten der drei Aggregatzuständen liegt im Aufbau der jeweiligen Materie. Im **Festkörper** sind die Atome und Moleküle starr angeordnet. Ihre Positionen sind über die Gitterstruktur des Festkörpers festgelegt. Die Atome und Moleküle bewegen sich aufgrund der immer vorhandenen thermischen Energie (Wärme) schwach um ihre Gitterpositionen.

Demgegenüber steht ihre lose Anordnung in einer **Flüssigkeit**. Die Atome und Moleküle ordnen sich ständig neu an.

In einem **Gas** bewegen sich die Atome und Moleküle sehr schnell und weisen eine hohe Bewegungsenergie (kinetische Energie) auf, die dafür sorgt, dass sie nicht zusammenhalten und sich im zur Verfügung stehenden Raum verteilen.

**\*Zur Information:** Feste und flüssige Stoffe werden als **kondensierte Materie** bezeichnet, Flüssigkeiten und Gas als **Fluide**.\*

**\*Gut zu wissen:** Ein Stoff kann von einem Aggregatzustand in einen anderen überführt werden. Diese Zustandsänderung erfolgt durch einen Phasenübergang, der sich beispielsweise durch eine Änderung der Temperatur, des Drucks oder des Volumens herbeiführen lässt.\*
Die verschiedenen Übergänge haben jeweils eigene Bezeichnungen:

| Übergang               | Bezeichnung         |
| ---------------------- | ------------------- |
| fest nach flüssig      | schmelzen           |
| fest nach gasförmig    | sublimieren         |
| flüssig nach gasförmig | verdampfen/sieden   |
| gasförmig nach flüssig | kondensieren        |
| gasförmig nach fest    | resublimieren       |
| flüssig nach fest      | erstarren/gefrieren |

Wir wissen nun, dass Materie in verschiedenen Aggregatzuständen vorkommen können – fest, flüssig und gasförmig – und dass ein Übergang zwischen den verschiedenen Zuständen durch Änderung verschiedener Parameter, wie Temperatur, Druck, Volumen etc. möglich ist. Ferner wissen wir, dass Materie aus Atomen bzw. Molekülen aufgebaut ist. Eine Frage, die wir uns jetzt noch stel-len könnten, betrifft die Frage nach der Anzahl an Atomen, die in einem bestimmten Volumen in den drei Aggregatszuständen ungefähr jeweils enthalten sind. Eine allgemein gültige Antwort kann nur grobe Werte geben, da die genauen Werte neben der jeweiligen Atom- oder Molekülsorte auch noch von den jeweils vorherrschenden Umgebungsbedingungen (Temperatur, Druck etc.) abhängen.

Aber als grobe Anhaltspunkte können für einen Würfel mit einer Kantenlänge von 1 mm, d. h. einem Volumen von 1 mm3, folgende Werte angeführt werden:

| Zustand   | Anazhal an Atomen       |
| --------- | ----------------------- |
| fest      | $10^{19}$ bis $10^{20}$ |
| flüssig   | $10^{19}$ bis $10^{20}$ |
| gasförmig | $10^{16}$ bis $10^{17}$ |

###### Übertrag der Strahlungsenergie auf Materie

Nun, da wir den Begriff Materie verstehen, betrachten wir die verschiedenen Arten, wie der Energieübertrag auf Materie für die verschiedenen Strahlungsarten erfolgt. Beginnen wir mit den gela-denen Teilchen, d. h. von α- und β-Strahlung, welche direkt ionisierend sind.

###### Direkte Ionisation

Schwere geladene Teilchen, wie α-Teilchen, wechselwirken mit Materie hauptsächlich über die **Coulombkraft**. Diese beschreibt die zwischen zwei Punktladungen wirkende Kraft, in unserem Fall zwischen der positiven Ladung des α-Teilchens und den negativen Ladungen der Elektronen der Atome in der Materie. Sobald ein α-Teilchen in Materie eindringt wechselwirkt es sofort mit einer Vielzahl an Elektronen. Ist der von einem α-Teilchen an ein Elektron übertragene Impuls ausreichend groß, dann kann hierdurch das Elektron aus dem Atom herausgelöst werden, d. h. es findet eine Ionisation des Atoms statt. Gleichzeitig reduziert sich die (Bewegungs-)Energie des α-Teilchens, da es ja einen Teil seiner Energie an das Elektron abgegeben hat.

Leichte geladene Teilchen, wie β-Teilchen, können Ihre (Bewegungs-)Energie ebenfalls über die Coulombkraft abgeben, zusätzlich aber auch noch durch Aussendung elektromagnetischer Strahlung: Wird ein sich bewegendes β-Teilchen aus seiner Flugrichtung abgelenkt, z. B. weil es in die Nähe eines Atomkernes gelangt, dann wird ein Teil seiner Energie in Strahlung umgewandelt, die sogenannte **Bremsstrahlung**. Diese kann durch anschließende indirekte Ionisation ihre Energie weiter an Materie abgeben.

###### Indirekte Ionisation

Gamma- und Röntgen-Strahlung sind elektrisch neutrale elektromagnetische Wellen (Photonen), weshalb sie mit Materie nicht direkt über die Coulombkraft wechselwirken. Deshalb werden sie auch als indirekt ionisierend bezeichnet. Ihre Wechselwirkung mit Materie erfolgt im Wesentlichen über die drei Prozesse

- **Photoelektrische Absorptio**n (meist als Photoeffekt bezeichnet),
- **Compton-Streuung** und
- **Paarbildung**.

Jeder dieser Prozesse führt zu einem teilweisen oder vollständigen Übertrag der Strahlungsenergie auf Elektronen der Materie.

###### Photoelektrischer Effekt

Im **photoelektrischen Effekt (Photoeffekt)** werden Elektronen durch die elektromagnetische Strahlung aus der Atomhülle herausgelöst. Die gesamte Energie der Strahlung geht an das Elektron in Form von Bewegungsenergie über, abzüglich der Energie, die für das Herauslösen des Elektrons aus seiner Bindung in der Atomhülle benötigt wird. Hieraus folgt, dass die Energie der elektromag-netischen Strahlung größer sein muss als die Bindungsenergie des Elektrons!

Die vollständige Absorption des Photons durch ein freies Elektron ist nicht möglich. Stattdessen findet ein Compton-Effekt statt, aus dem immer auch ein Photon geringerer Energie hervorgeht.

###### Compton-Streuung

Bei der **Compton-Streuung (Compton-Effekt)** wird die elektromagnetische Strahlung an einem Elektron gestreut. Hierbei geht ein Teil der Energie der Strahlung auf das Elektron über, das aus der Atomhülle herausgelöst wurde. Die Energie der gestreuten elektromagnetischen Strahlung ist dann entsprechend geringer.

Die Compton-Streuung ist der dominierende Wechselwirkungsprozess für elektromagnetische Strahlung mit Materie zwischen etwa 100 keV und 10 MeV.

###### Paarbildung

Ist die Energie der elektromagnetischen Strahlung höher als 1022 keV, dann kann in der Nähe von Atomkernen die gesamte Energie in Masse sowie Bewegungsenergie in Form eines Elektron-Positron-Paares umgewandelt werden (**Paarbildung**). Die Ruhemasse eines Elektrons bzw. Positrons beträgt jeweils 511 keV, d. h. es wird mindestens eine Energie von 1022 keV für die Erzeugung der beiden Teilchen aus der elektromagnetischen Strahlung benötigt. Der verbleibende Rest der Energie wird auf die beiden Teilchen in Form von Bewegungsenergie aufgeteilt, mit der sie sich in einander entgegengesetzte Richtungen fortbewegen.

###### Ionisation durch Neutronen

Neutronen-Strahlung bildet einen speziellen Fall indirekter Ionisation. Die ungeladenen Neutronen können zum Teil weit in Materie eindringen und dort durch Stöße mit Atomkernen Bewegungsenergie übertragen oder aber Kernreaktionen initiieren.

Im Fall eines Stoßes kann die gesamte oder ein Teil der Energie des Neutrons an einen Atomkern übertragen werden, der als geladenes (schweres) Teilchen weiterfliegt. Findet eine Kernreaktion statt, dann wird das Neutron von dem Atomkern absorbiert und es entsteht ebenfalls ein geladenes schweres Teilchen. Die geladenen Teilchen können wiederum direkte Ionisation durchführen.

###### Schwächung von Strahlung

Nun wissen wir, auf welche Weise Strahlung mit Materie in Wechselwirkung tritt. Einen wichtigen Punkt haben wir aber nur kurz angerissen: Die Frage, wie stark sind diese Wechselwirkungen, oder anders formuliert, wie weit dringt die Strahlung in Materie ein. Aus der Beantwortung dieser Frage leiten sich die im Strahlenschutz zu treffenden Maßnahmen ab: Je weiter eine Strahlung in Materie eindringen kann, desto größere Anstrengungen bezüglich der erforderlichen Abschirmungen sind zu treffen.

Die Größen, die in diesem Zusammenhang eine wichtige Rolle spielen, sind die sogenannten **Wirkungsquerschnitte**. Der Wirkungsquerschnitt ist ein Maß für die Wahrscheinlichkeit einer bestimmten Wechselwirkung einer Strahlung mit einem bestimmten Stoff (Materie), d. h. wie wahrscheinlich ist es, dass ein α-Teilchen an einer bestimmten Atomsorte gestreut wird, oder Gamma-Strahlung in einem bestimmten Material einen Photoeffekt ausführt, oder ein Neutron von einem Atom in einer Kernreaktion absorbiert wird …

Die Werte der Wirkungsquerschnitte sind für die verschiedenen Strahlenarten für verschiedene Materialien und Strahlenenergien tabelliert.

- Nuclear Data Center, Japan Atomic Energy Agency [https://wwwndc.jaea.go.jp/NuC/](https://wwwndc.jaea.go.jp/NuC/)
- Live Chart of Nuclides, IAEA, [https://www-nds.iaea.org/relnsd/vcharthtml/VChartHTML.html](https://www-nds.iaea.org/relnsd/vcharthtml/VChartHTML.html)
- X-Ray and Gamma-Ray Data, NIST, [https://www.nist.gov/pml/x-ray-and-gamma-ray-data](https://www.nist.gov/pml/x-ray-and-gamma-ray-data)

Wie bereits erwähnt, liegen die Reichweiten von α-Strahlen in Luft bei wenigen Zentimetern, in Gewebe bei einigen Mikrometern. Bereits ein Blatt Papier oder die Hautoberfläche reichen zu ihrer Abschirmung aus.

Für β-Strahlung ist die Reichweite größer. Sie liegt in Luft bei maximal wenigen Metern, in Gewebe bei wenigen Millimetern. Hier ist ein dünnes Blech (z. B. aus Aluminium) zu ihrer Abschirmung ausreichend.

Bei Röntgen- und Gamma-Strahlung bzw. Neutronen müssen wir aber tatsächlich die Energie der Strahlung und das Material, mit dem sie wechselwirken, und damit den jeweiligen Wirkungsquerschnitt kennen, um eine Aussage über ihre Reichweite treffen zu können.

Dann können wir in guter Näherung mit der Gleichung

$I = I_0 \cdot exp(-µ \cdot x)$

die Strahlungsintensität $I$ berechnen, die sich hinter einem Material der Dicke $x$ mit dem Wirkungsquerschnitt (genauer: dem linearen Schwächungskoeffizienten) $µ$ ergibt, wenn die Strahlungsintensität beim Eindringen in das Material $I_0$ war.

Für den praktischen Strahlenschutz hat das folgende Auswirkungen:

- Wir können somit bei Kenntnis der Parameter $I_0$, $µ$ und $x$ eine Aussage treffen, wie hoch die Strahlungsintensität hinter einem Material ist, beispielsweise hinter einer Wand, einer Türe, einer Abschirmung etc. und ob wir gegebenenfalls weitere Abschirmmaßnahmen treffen müssen.
- Die Strahlungsintensität nimmt exponentiell ab. Das bedeutet aber, dass sie niemals völlig verschwunden sein wird. Wir können aber durch geeignete Abschirmmaßnahmen dafür Sorge tragen, dass sie so gering wird, dass sie keine gesundheitsschädlichen oder sonstigen Auswirkungen mit sich bringt. Dies kann durch geeignete Wahl des Materials (legt den Wirkungsquerschnitt fest) und dessen Dicke erfolgen.

**\*Anmerkung:** Bei einer Schwächung durch Ionisation kann, wie wir gesehen haben, sogenannte Sekundärstrahlung entstehen. Deren Auswirkungen sind dann ebenfalls zu berücksichtigt.\*

#### Questions (practice / free-response)

```yaml
- id: m4-q1
  prompt: "Was versteht man unter Wechselwirkung ionisierender Strahlung mit Materie?"
  reference_answer: "Trifft Strahlung (z. B. α-, β-, γ- oder Neutronen-Strahlung) auf Materie (z. B. ein Gas, eine Flüssigkeit oder einen Festkörper), dann wird die Energie dieser Strahlung ganz oder teilweise auf die Materie übertragen. Dieser Übertrag kann durch Stöße (z. B. Ionisation, Anregung) oder Umwandlungsprozesse (z. B. Compton-Streuung, Photoeffekt, Paarbildung) stattfinden und wird allgemein als Wechselwirkung der Strahlung mit Materie bezeichnet."
  points: 1

- id: m4-q2
  prompt: "Welche Aggregatzustände der Materie gibt es?"
  reference_answer: "Die drei Zustände fest, flüssig und gasförmig bilden die klassischen Aggregatzustände der Materie."
  points: 1

- id: m4-q3
  prompt: "Welche zwei Arten des Übertrags von Strahlungsenergie auf Materie kennen Sie?"
  reference_answer: "Ein Übertrag von Strahlungsenergie auf Materie erfolgt durch Ionisation. Hier unterscheidet man zwischen direkter und indirekter Ionisation."
  points: 1

- id: m4-q4
  prompt: "Welche Kraft ist für die direkte Ionisation hauptsächlich verantwortlich?"
  reference_answer: "Bei der direkten Ionisation wirkt hauptsächlich die Coulombkraft zwischen der Strahlung, die aus geladenen Teilchen besteht (z. B. α- und β-Teilchen) und den Elektronen der Atomhülle der Materie."
  points: 1

- id: m4-q5
  prompt: "Welche Wechselwirkungsprozesse treten hauptsächlich bei der indirekten Ionisation auf?"
  reference_answer: "Die Wechselwirkung mit Materie erfolgt im Wesentlichen über die drei Prozesse Photoelektrische Absorption (meist als Photoeffekt bezeichnet), Compton-Streuung und Paarbildung."
  points: 1

- id: m4-q6
  prompt: "Beschreiben Sie den Prozess des Photoeffekts."
  reference_answer: "Im photoelektrischen Effekt (Photoeffekt) werden Elektronen durch die elektromagnetische Strahlung aus der Atomhülle herausgelöst. Die gesamte Energie der Strahlung geht an das Elektron in Form von Bewegungsenergie über, abzüglich der Energie, die für das Herauslösen des Elektrons aus seiner Bindung in der Atomhülle benötigt wird. Hieraus folgt, dass die Energie der elektromag-netischen Strahlung größer sein muss als die Bindungsenergie des Elektrons!"
  points: 1

- id: m4-q7
  prompt: "Beschreiben Sie den Prozess der Compton-Streuung."
  reference_answer: "Bei der Compton-Streuung (Compton-Effekt) wird die elektromagnetische Strahlung an einem Elektron gestreut. Hierbei geht ein Teil der Energie der Strahlung auf das Elektron über, das aus der Atomhülle herausgelöst wurde. Die Energie der gestreuten elektromagnetischen Strahlung ist dann entsprechend geringer."
  points: 1

- id: m4-q8
  prompt: "Beschreiben Sie den Prozess der Paarbildung."
  reference_answer: "Ist die Energie der elektromagnetischen Strahlung höher als 1022 keV, dann kann in der Nähe von Atomkernen die gesamte Energie in Masse sowie Bewegungsenergie in Form eines Elektron-Positron-Paares umgewandelt werden (Paarbildung). Die Ruhemasse eines Elektrons bzw. Posit-rons beträgt jeweils 511 keV, d. h. es wird mindestens eine Energie von 1022 keV für die Erzeu-gung der beiden Teilchen aus der elektromagnetischen Strahlung benötigt. Der verbleibende Rest der Energie wird auf die beiden Teilchen in Form von Bewegungsenergie aufgeteilt, mit der sie sich in einander entgegengesetzte Richtungen fortbewegen."
  points: 1

- id: m4-q9
  prompt: "Erklären Sie die Bedeutung des Begriffs Wirkungsquerschnitt."
  reference_answer: "Der Wirkungsquerschnitt ist ein Maß für die Wahrscheinlichkeit einer bestimmten Wechselwirkung einer Strahlung mit einem bestimmten Stoff (Materie)"
  points: 1
```

#### Quiz (auto-graded)

```yaml
meta:
  id: m4-quiz
  title: "Module 4 quiz"
  pass_percent: 70
items:
  - id: m4-quiz1
    type: multi_select
    prompt: "Was hat jegliche Strahlung? (wählen Sie bitte eine Antwort aus)"
    points: 1
    choices:
      - id: a1
        text: "Eine Ursache"
        correct: true
        feedback: "Ihre Antwort ist korrekt."
      - id: a2
        text: "Eine Farbe"
        correct: false
        feedback: 'Ihre Antwort ist nicht richtig. Lesen Sie den Abschnitt "Was ist Strahlung?" nochmals genau durch.'
      - id: a3
        text: "Eine Wirkung"
        correct: true
        feedback: "Ihre Antwort ist korrekt."
```

#### Further reading

- [Strahlenschutzgesetz](https://www.gesetze-im-internet.de/strlschg/)

#### Common misconceptions

```yaml
- misconception:
  correction:

- misconception:
  correction:
```

#### Grade

```yaml
completion:
  required: true
  passing_percent: 70
grade_items:
  - id: m4-quiz
    points_total: 1
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
    prompt: "Der Begriff „Tätigkeit“ ist im Strahlenschutzgesetz in § 4 definiert."
    points: 1
    answer: true

  - id: final-quiz2
    type: true_false
    prompt: "Nukleonen sind Protonen und Neutronen."
    points: 1
    answer: true

  - id: final-quiz3
    type: true_false
    prompt: "Ionisierende Strahlung kann durch Wechselwirkung Elektronen aus Atomen oder Molekülen freisetzen (Ionisation)."
    points: 1
    answer: true

  - id: final-quiz4
    type: true_false
    prompt: "Compton-Streuung ist ein typischer Wechselwirkungsprozess von Photonen mit Elektronen in Materie."
    points: 1
    answer: true
```

<!-- Course contents End -->
