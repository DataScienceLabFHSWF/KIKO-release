---
schema: course.v1

course:
  id: introduction-to-climate-change-the-science-of-warming
  source_doc: "climate.md"
  title: "Introduction to Climate Change: The Science of Warming"
  version: "1.0"
  provider: "Course Team"
  language: English
  level: Beginner
  tags: [climate-change, climate-science, greenhouse-effect, weather, climate, ghg]
  estimated_minutes: 25
  published: true
  prerequisites: []

instructors:
  - id: inst-1
    name: "Course Team"
    bio: "Introductory course on climate science fundamentals, the greenhouse effect, greenhouse gases, and evidence of global warming."

grading:
  pass_percent: 70
  assessment_weights:
    m1: 0.15
    m2: 0.15
    m3: 0.15
    m4: 0.15
    final_quiz: 0.40
  policy:
    calculation:
      type: weighted_modules
      weights_ref: "grading.assessment_weights"
    completion:
      required_modules: [m1, m2, m3, m4]
      required_assessments: [final-quiz]
      assessment_pass_percent: 70
    notes:
      - "The final grade is the weighted average of the module quizzes and the final quiz."
      - "All four modules and the final quiz must be completed to finish the course."

resources:
  - id: res-1
    title: "IPCC Sixth Assessment Report"
    type: link
    url: "https://www.ipcc.ch/assessment-report/ar6/"
  - id: res-2
    title: "NASA: Global Climate Change"
    type: link
    url: "https://science.nasa.gov/climate-change/"
  - id: res-3
    title: "NOAA Climate.gov"
    type: link
    url: "https://www.noaa.gov/climate"
---

<!-- Course contents start -->

# Introduction to Climate Change: The Science of Warming

## Course overview

This course introduces core climate science concepts needed to understand modern global warming. It explains the difference between weather and climate, the natural greenhouse effect, the main greenhouse gases, and the key indicators showing that the climate is changing.

### Learning outcomes

- Distinguish clearly between weather and climate.
- Explain how the greenhouse effect works and why it is essential for life on Earth.
- Identify the major greenhouse gases and describe how human activities increase them.
- Recognize major lines of evidence for a warming world.

## Modules

### Module 1: Weather vs. Climate {#m1}

#### Content

##### Weather vs. Climate

A fundamental distinction in environmental science is the difference between weather and climate.

> **Weather** refers to short-term atmospheric conditions (rain, temperature, wind) at a specific time and place. **Climate** is the statistical average of weather patterns over a long period, typically defined by the World Meteorological Organization (WMO) as 30 years or more.

#### Questions (practice / free-response)

```yaml
- id: m1-q1
  prompt: "What is the difference between weather and climate?"
  reference_answer: "Weather refers to short-term atmospheric conditions at a specific time and place, while climate is the long-term statistical average of weather patterns over 30 years or more."
  points: 1

- id: m1-q2
  prompt: "Why is climate not the same as a single hot or cold day?"
  reference_answer: "Because climate describes long-term patterns and averages, not isolated short-term weather events."
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
    prompt: "Which statement best defines climate?"
    points: 1
    choices:
      - id: a1
        text: "The average pattern of weather over a long period."
        correct: true
        feedback: "Correct. Climate refers to the long-term statistical average of weather patterns."
      - id: a2
        text: "The temperature and rainfall at one place during one afternoon."
        correct: false
        feedback: "Incorrect. That describes weather, not climate."
      - id: a3
        text: "Any unusual storm event."
        correct: false
        feedback: "Incorrect. A single event is weather, not climate."

  - id: m1-quiz2
    type: mcq
    prompt: "What does weather refer to?"
    points: 1
    choices:
      - id: a1
        text: "Short-term atmospheric conditions at a specific time and place."
        correct: true
        feedback: "Correct. That is the definition given in the lesson."
      - id: a2
        text: "The 100-year trend of temperatures across the whole planet."
        correct: false
        feedback: "Incorrect. That would describe climate, not weather."
      - id: a3
        text: "Only long-term rainfall averages."
        correct: false
        feedback: "Incorrect. Weather includes short-term conditions such as rain, temperature, and wind."
```

#### Further reading

- [NOAA Climate.gov](https://www.noaa.gov/climate)
- [NASA: Global Climate Change](https://science.nasa.gov/climate-change/)

#### Common misconceptions

```yaml
- misconception: "Weather and climate mean the same thing."
  correction: "The lesson distinguishes them clearly: weather is short-term, while climate refers to long-term averages and patterns."

- misconception: "A single cold day disproves climate change."
  correction: "A single day is weather. Climate is assessed from long-term patterns over decades."
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

### Module 2: The Greenhouse Effect {#m2}

#### Content

##### The Greenhouse Effect

The Earth remains habitable due to the natural greenhouse effect. Solar radiation reaches the Earth; some is reflected back to space, but much is absorbed, warming the planet. The Earth then emits this energy as infrared radiation (heat).

![Visualizing how greenhouse gases trap solar heat in the atmosphere.](/api/course/{{COURSE_ID}}/images/climate_change_course_1_greenhouse.png)

Greenhouse gases (GHGs) in the atmosphere absorb and re-radiate this infrared energy, trapping heat in the lower atmosphere. Without this natural process, Earth's average temperature would be approximately $-18^\circ\text{C}$ instead of the current $+15^\circ\text{C}$.

#### Questions (practice / free-response)

```yaml
- id: m2-q1
  prompt: "Why is the natural greenhouse effect important for life on Earth?"
  reference_answer: "It keeps Earth warm enough for life by trapping some outgoing infrared radiation in the lower atmosphere. Without it, the average temperature would be about -18°C instead of about +15°C."
  points: 1

- id: m2-q2
  prompt: "How do greenhouse gases warm the lower atmosphere?"
  reference_answer: "They absorb and re-radiate infrared energy emitted by Earth, which traps heat in the lower atmosphere."
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
    prompt: "What does the natural greenhouse effect do?"
    points: 1
    choices:
      - id: a1
        text: "It helps keep Earth warm enough for life by trapping heat in the lower atmosphere."
        correct: true
        feedback: "Correct. The greenhouse effect keeps Earth habitable by trapping some infrared heat."
      - id: a2
        text: "It blocks all incoming solar radiation from reaching Earth."
        correct: false
        feedback: "Incorrect. Some solar radiation is reflected, but much is absorbed by Earth."
      - id: a3
        text: "It removes all greenhouse gases from the air."
        correct: false
        feedback: "Incorrect. Greenhouse gases are what make the greenhouse effect possible."

  - id: m2-quiz2
    type: mcq
    prompt: "Without the natural greenhouse effect, Earth's average temperature would be approximately:"
    points: 1
    choices:
      - id: a1
        text: "-18°C"
        correct: true
        feedback: "Correct. The lesson states that without the natural greenhouse effect, Earth's average temperature would be about -18°C."
      - id: a2
        text: "+15°C"
        correct: false
        feedback: "Incorrect. +15°C is the approximate current average temperature with the natural greenhouse effect."
      - id: a3
        text: "+50°C"
        correct: false
        feedback: "Incorrect. That is not the value given in the lesson."
```

#### Further reading

- [IPCC Sixth Assessment Report](https://www.ipcc.ch/assessment-report/ar6/)
- [NASA: Global Climate Change](https://science.nasa.gov/climate-change/)

#### Common misconceptions

```yaml
- misconception: "The greenhouse effect is entirely unnatural."
  correction: "The lesson explains that the natural greenhouse effect is essential for life; the problem is that human activities are intensifying it."

- misconception: "Greenhouse gases only reflect sunlight away from Earth."
  correction: "The lesson states that greenhouse gases absorb and re-radiate infrared energy emitted by Earth, trapping heat."
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

### Module 3: Key Greenhouse Gases {#m3}

#### Content

##### Key Greenhouse Gases

Human activities have increased the concentration of these gases, intensifying the greenhouse effect (Global Warming). The primary gases are:

1. **Carbon Dioxide ($CO_2$):** Released through burning fossil fuels (coal, oil, natural gas), deforestation, and cement production. It is responsible for the majority of anthropogenic radiative forcing.
2. **Methane ($CH_4$):** Emitted during the production of coal, natural gas, and oil, as well as from livestock and agricultural practices. $CH_4$ is roughly 25 times more potent than $CO_2$ at trapping heat over a 100-year period.
3. **Nitrous Oxide ($N_2O$):** emitted during agricultural and industrial activities, combustion of fossil fuels and solid waste.

![Correlation between rising atmospheric CO₂ and global temperatures.](/api/course/{{COURSE_ID}}/images/climate_change_course_2_changes.png)

#### Questions (practice / free-response)

```yaml
- id: m3-q1
  prompt: "Name the three primary greenhouse gases highlighted in this lesson."
  reference_answer: "Carbon dioxide (CO2), methane (CH4), and nitrous oxide (N2O)."
  points: 1

- id: m3-q2
  prompt: "Give two major human sources of carbon dioxide."
  reference_answer: "Major human sources include burning fossil fuels and deforestation. Cement production is another source mentioned in the lesson."
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
    prompt: "Which statement accurately describes the relationship between Methane (CH4) and Carbon Dioxide (CO2) regarding global warming?"
    points: 1
    choices:
      - id: a1
        text: "Methane is more abundant in the atmosphere than CO2."
        correct: false
        feedback: "Incorrect. CO2 is much more abundant in the atmosphere than methane."
      - id: a2
        text: "Methane stays in the atmosphere longer than CO2."
        correct: false
        feedback: "Incorrect. The lesson notes that methane is shorter-lived than CO2."
      - id: a3
        text: "Methane is a more potent heat-trapping gas per molecule than CO2."
        correct: true
        feedback: "Correct. Methane is more potent per molecule, even though it is present in smaller quantities."

  - id: m3-quiz2
    type: mcq
    prompt: "Which of the following is listed as a source of CO2 in the lesson?"
    points: 1
    choices:
      - id: a1
        text: "Burning fossil fuels"
        correct: true
        feedback: "Correct. The lesson identifies fossil fuel combustion as a major source of CO2."
      - id: a2
        text: "Only volcanic eruptions"
        correct: false
        feedback: "Incorrect. The lesson specifically highlights human sources such as fossil fuels, deforestation, and cement production."
      - id: a3
        text: "Magnetic confinement of plasma"
        correct: false
        feedback: "Incorrect. That is unrelated to greenhouse gas emissions in this course."
```

#### Further reading

- [IPCC Sixth Assessment Report](https://www.ipcc.ch/assessment-report/ar6/)
- [NOAA Climate.gov](https://www.noaa.gov/climate)

#### Common misconceptions

```yaml
- misconception: "Methane matters less because there is less of it in the atmosphere."
  correction: "The lesson explains that methane is much more potent per molecule at trapping heat, even though it is less abundant than CO2."

- misconception: "CO2 comes only from natural sources."
  correction: "The lesson identifies fossil fuel burning, deforestation, and cement production as major human sources of CO2."
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

### Module 4: Evidence of Climate Change {#m4}

#### Content

##### Evidence of Change

Key indicators of a warming world include rising global average temperatures, shrinking ice sheets, retreating glaciers, and ocean acidification (caused by the absorption of $CO_2$ into the oceans).

#### Questions (practice / free-response)

```yaml
- id: m4-q1
  prompt: "What are two indicators mentioned in the lesson that show the world is warming?"
  reference_answer: "Examples include rising global average temperatures, shrinking ice sheets, retreating glaciers, and ocean acidification."
  points: 1

- id: m4-q2
  prompt: "Why does ocean acidification appear in a lesson about climate change?"
  reference_answer: "Because it is linked to the absorption of CO2 by the oceans and is presented as one of the key indicators of human-driven environmental change."
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
    type: mcq
    prompt: "Which of the following is identified as evidence of a warming world?"
    points: 1
    choices:
      - id: a1
        text: "Retreating glaciers"
        correct: true
        feedback: "Correct. Retreating glaciers are listed as one indicator of climate change."
      - id: a2
        text: "A single storm in one city"
        correct: false
        feedback: "Incorrect. The lesson focuses on broad climate indicators, not a single weather event."
      - id: a3
        text: "A decrease in all atmospheric gases"
        correct: false
        feedback: "Incorrect. That is not described in the lesson."

  - id: m4-quiz2
    type: mcq
    prompt: "What causes ocean acidification according to the lesson?"
    points: 1
    choices:
      - id: a1
        text: "The absorption of CO2 into the oceans"
        correct: true
        feedback: "Correct. The lesson links ocean acidification to the absorption of CO2 by the oceans."
      - id: a2
        text: "The freezing of seawater into glaciers"
        correct: false
        feedback: "Incorrect. That is not the cause given in the lesson."
      - id: a3
        text: "Natural greenhouse gases leaving the atmosphere"
        correct: false
        feedback: "Incorrect. That is not described in the course content."
```

#### Further reading

- [NASA: Global Climate Change](https://science.nasa.gov/climate-change/)
- [IPCC Sixth Assessment Report](https://www.ipcc.ch/assessment-report/ar6/)

#### Common misconceptions

```yaml
- misconception: "Climate change can only be detected from air temperature records."
  correction: "The lesson also identifies shrinking ice sheets, retreating glaciers, and ocean acidification as important indicators."

- misconception: "Ocean acidification is unrelated to atmospheric CO2."
  correction: "The lesson explicitly links ocean acidification to the absorption of CO2 into the oceans."
```

#### Grade

```yaml
completion:
  required: true
  passing_percent: 70
grade_items:
  - id: m4-quiz
    points_total: 2
```

## Overall Quiz

```yaml
meta:
  id: final-quiz
  title: "Final quiz"
  points_total: 4
  pass_percent: 70
items:
  - id: final-quiz1
    type: true_false
    prompt: "Weather refers to short-term atmospheric conditions, while climate refers to long-term average patterns."
    points: 1
    answer: true

  - id: final-quiz2
    type: true_false
    prompt: "The natural greenhouse effect is essential because it helps keep Earth warm enough for life."
    points: 1
    answer: true

  - id: final-quiz3
    type: true_false
    prompt: "Methane is identified in the course as a more potent heat-trapping gas per molecule than CO2."
    points: 1
    answer: true

  - id: final-quiz4
    type: true_false
    prompt: "Retreating glaciers and ocean acidification are presented as indicators of climate change."
    points: 1
    answer: true
```

<!-- Course contents End -->
