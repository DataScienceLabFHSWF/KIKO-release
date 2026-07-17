---
schema: course.v1

course:
  id: small-modular-reactors-explained
  source_doc: "smr.md"
  title: "Small Modular Reactors (SMRs) Explained"
  version: "1.0"
  provider: "Course Team"
  language: English
  level: Intermediate
  tags: [nuclear-energy, smr, reactors, safety, decarbonization, eu-policy]
  estimated_minutes: 20
  published: true
  prerequisites: []

instructors:
  - id: inst-1
    name: "Course Team"
    bio: "Introductory course on small modular reactors, their advantages, safety features, and deployment context."

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
      - "The final grade is the weighted average of the module quizzes and the final quiz."
      - "All three modules and the final quiz must be completed to finish the course."

resources:
  - id: res-1
    title: "European Commission: Small Modular Reactors Explained"
    type: link
    url: "https://energy.ec.europa.eu/topics/nuclear-energy/small-modular-reactors/small-modular-reactors-explained_en"
  - id: res-2
    title: "IAEA: Small Modular Reactors"
    type: link
    url: "https://www.iaea.org/topics/small-modular-reactors"
  - id: res-3
    title: "European Commission: SMRs at international level"
    type: link
    url: "https://energy.ec.europa.eu/topics/nuclear-energy/small-modular-reactors_en#smrs-at-international-level"
---

<!-- Course contents start -->

# Small Modular Reactors (SMRs) Explained

## Course overview

This course introduces Small Modular Reactors (SMRs), their defining technical characteristics, their economic and operational advantages, their passive safety features, and the broader international and European context for deployment.

### Learning outcomes

- Define Small Modular Reactors (SMRs) and their output capacity.
- Identify the economic and operational advantages of SMRs.
- Understand the passive safety features of SMR technology.
- Describe the global and EU landscape for SMR deployment.

## Modules

### Module 1: What are SMRs? {#m1}

#### Content

##### Definition and Output Capacity

Small modular reactors (SMRs) are defined as small nuclear reactors with a maximum electrical output of 300 Megawatts (MWe).

![SMR: Small Modular Reactors.](/api/course/{{COURSE_ID}}/images/SMR_course_1_title.png)

To put this in perspective:

- **SMRs:** Produce up to 7.2 million kWh per day.
- **Large-size nuclear plants:** Typically have an output of over 1,000 MWe and produce 24 million kWh per day.

![Comparing the footprint: SMRs versus traditional nuclear plants.](/api/course/{{COURSE_ID}}/images/SMR_course_2_comparison.jpg)

##### Size Range and Technology Options

SMRs vary in size from around 20 MWe up to 300 MWe. While they all use nuclear fission to generate heat, they can utilize various coolants, including light water, liquid metal, or molten salt. Reactors based on non-light water technology are often referred to as Advanced Modular Reactors (AMRs).

#### Questions (practice / free-response)

```yaml
- id: m1-q1
  prompt: "How is an SMR defined in terms of electrical output?"
  reference_answer: "An SMR is defined as a small nuclear reactor with a maximum electrical output of 300 MWe."
  points: 1

- id: m1-q2
  prompt: "What are two coolant options that SMRs can use?"
  reference_answer: "SMRs can use light water, liquid metal, or molten salt."
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
    prompt: "What is the maximum electrical output that defines a Small Modular Reactor (SMR)?"
    points: 1
    choices:
      - id: a1
        text: "300 Megawatts electric (MWe)"
        correct: true
        feedback: "Correct. SMRs are defined as having a maximum output of 300 MWe."
      - id: a2
        text: "1,000 Megawatts electric (MWe)"
        correct: false
        feedback: "Incorrect. 1,000 MWe is typical for a large-size nuclear power plant."
      - id: a3
        text: "50 Megawatts electric (MWe)"
        correct: false
        feedback: "Incorrect. While SMRs can be as small as 20 MWe, the definition includes reactors up to 300 MWe."

  - id: m1-quiz2
    type: mcq
    prompt: "What term is often used for reactors based on non-light water technology?"
    points: 1
    choices:
      - id: a1
        text: "Advanced Modular Reactors (AMRs)"
        correct: true
        feedback: "Correct. Non-light water SMR technologies are often referred to as AMRs."
      - id: a2
        text: "Conventional Thermal Units (CTUs)"
        correct: false
        feedback: "Incorrect. That term is not used here."
      - id: a3
        text: "Expanded Fission Systems (EFSs)"
        correct: false
        feedback: "Incorrect. That term is not used in the lesson."
```

#### Further reading

- [European Commission: Small Modular Reactors Explained](https://energy.ec.europa.eu/topics/nuclear-energy/small-modular-reactors/small-modular-reactors-explained_en)
- [IAEA: Small Modular Reactors](https://www.iaea.org/topics/small-modular-reactors)

#### Common misconceptions

```yaml
- misconception: "SMRs are a completely different energy source from nuclear fission."
  correction: "SMRs still use nuclear fission to generate heat; they mainly differ in size, modularity, and reactor design choices."

- misconception: "Any reactor below 50 MWe is the only type counted as an SMR."
  correction: "SMRs span a range from about 20 MWe up to 300 MWe."
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

### Module 2: Advantages and Applications of SMRs {#m2}

#### Content

##### Key Advantages

The economics and business cases for SMRs differ significantly from traditional large-scale nuclear plants.

- **Decarbonization & Grid Stability:** SMRs contribute to the EU Green Deal objectives and help ensure grid stability in systems with high shares of renewables.
- **Flexibility & Footprint:** Due to their smaller size and capacity, they require less space and less cooling water, allowing for greater flexibility in site selection compared to large plants.
- **Modularity:** Systems can be factory-assembled and transported as modules or whole units, reducing installation costs. This allows for production cost efficiency through economies of scale.
- **Industrial Applications:** Beyond electricity, SMRs can supply heat for district heating, industrial processes, and hydrogen production.
- **Job Retention:** They are well-suited to replace fossil fuel-fired plants, helping retain high-skilled jobs in affected areas.

![Reactor design featuring passive cooling and grid integration.](/api/course/{{COURSE_ID}}/images/SMR_course_3_figure.jpg)

#### Questions (practice / free-response)

```yaml
- id: m2-q1
  prompt: "Why are SMRs considered flexible regarding site selection?"
  reference_answer: "Because they are smaller in size and power output, they require less physical space and less cooling water than large plants, allowing them to be built in more locations."
  points: 1

- id: m2-q2
  prompt: "Apart from generating electricity, what are two other applications for the heat generated by SMRs?"
  reference_answer: "The heat from SMRs can be used for district heating, industrial processes, or the production of hydrogen."
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
    prompt: "How do SMRs contribute to economic efficiency?"
    points: 1
    choices:
      - id: a1
        text: "Through factory assembly and modularity (economies of scale)."
        correct: true
        feedback: "Correct. Factory assembly reduces installation costs and allows for serial production."
      - id: a2
        text: "By requiring larger land areas for construction."
        correct: false
        feedback: "Incorrect. SMRs require less space than traditional plants."
      - id: a3
        text: "By strictly using only light water technology."
        correct: false
        feedback: "Incorrect. SMRs can use various coolants, and the choice of coolant is not the primary driver of their economic modularity."

  - id: m2-quiz2
    type: mcq
    prompt: "Which of the following is listed as a non-electric application of SMRs?"
    points: 1
    choices:
      - id: a1
        text: "District heating"
        correct: true
        feedback: "Correct. The lesson explicitly mentions district heating as an application."
      - id: a2
        text: "Only desalination of seawater"
        correct: false
        feedback: "Incorrect. That is not the application highlighted in the lesson."
      - id: a3
        text: "Only battery manufacturing"
        correct: false
        feedback: "Incorrect. That is not one of the applications listed in the lesson."
```

#### Further reading

- [European Commission: Small Modular Reactors Explained](https://energy.ec.europa.eu/topics/nuclear-energy/small-modular-reactors/small-modular-reactors-explained_en)
- [European Commission: SMRs at international level](https://energy.ec.europa.eu/topics/nuclear-energy/small-modular-reactors_en#smrs-at-international-level)

#### Common misconceptions

```yaml
- misconception: "SMRs are useful only for electricity generation."
  correction: "SMRs can also provide district heating, industrial heat, and hydrogen production."

- misconception: "Smaller reactors automatically mean weaker economic potential."
  correction: "SMRs are designed to benefit from modularity, factory assembly, and potentially lower installation costs."
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

### Module 3: Safety Features and Deployment Context {#m3}

#### Content

##### Safety Features

SMRs incorporate passive (inherent) safety systems and leverage operating experience from traditional reactors and nuclear submarines.

These passive safety principles often rely on simple phenomena, such as **natural circulation** for cooling the reactor core. This design allows the reactor to be brought to a safe state during incidents with very limited or no operator action.

Furthermore, these systems allow for the elimination of various components—such as specific pumps, cables, and valves—which effectively limits the risk of component failure.

##### Global and EU Action

**Global Context**
There are currently more than 80 SMR designs in development across 18 countries. While nations like the U.S., UK, Canada, and Japan are developing designs, Russia (2019) and China (2021) have already connected their first SMRs to the grid.

**EU Context**
The EU supports SMR development through the **Euratom Research and Training Programme (2021-2025)**, focusing on safety, waste management, and skills. To support deployment by the early 2030s, the Commission launched the **European SMR Industrial Alliance** in February 2024.

#### Questions (practice / free-response)

```yaml
- id: m3-q1
  prompt: "Why are passive safety systems considered an advantage in SMR design?"
  reference_answer: "Because they can bring the reactor to a safe state during incidents with very limited or no operator action, often by relying on simple physical phenomena such as natural circulation."
  points: 1

- id: m3-q2
  prompt: "What is the European SMR Industrial Alliance?"
  reference_answer: "It is an initiative launched by the European Commission in February 2024 to support the successful deployment of the first SMR projects in Europe by the early 2030s."
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
    prompt: "Which of the following is a primary safety advantage of SMRs?"
    points: 1
    choices:
      - id: a1
        text: "They rely on passive safety systems like natural circulation."
        correct: true
        feedback: "Correct. Passive systems allow the reactor to cool without active operator intervention."
      - id: a2
        text: "They require more cooling water than large plants."
        correct: false
        feedback: "Incorrect. SMRs actually require less cooling water."
      - id: a3
        text: "They use complex active pumping systems."
        correct: false
        feedback: "Incorrect. SMRs aim to eliminate complex active components like safety grade pumps to reduce failure risks."

  - id: m3-quiz2
    type: mcq
    prompt: "What did the European Commission launch in February 2024 to support SMR deployment?"
    points: 1
    choices:
      - id: a1
        text: "The European SMR Industrial Alliance"
        correct: true
        feedback: "Correct. The Alliance was launched to support deployment by the early 2030s."
      - id: a2
        text: "The European Fossil Transition Board"
        correct: false
        feedback: "Incorrect. That is not the initiative named in the lesson."
      - id: a3
        text: "The Euratom Grid Shutdown Mechanism"
        correct: false
        feedback: "Incorrect. That is not the initiative named in the lesson."
```

#### Further reading

- [IAEA: Small Modular Reactors](https://www.iaea.org/topics/small-modular-reactors)
- [European Commission: SMRs at international level](https://energy.ec.europa.eu/topics/nuclear-energy/small-modular-reactors_en#smrs-at-international-level)

#### Common misconceptions

```yaml
- misconception: "Passive safety means no safety engineering is needed."
  correction: "Passive safety means the design relies more on inherent physical processes and fewer active components, not that safety engineering is absent."

- misconception: "SMRs are already widely deployed everywhere."
  correction: "Many designs are still under development, although some countries such as Russia and China have already connected early SMR units to the grid."
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
  title: "Final quiz"
  points_total: 4
  pass_percent: 70
items:
  - id: final-quiz1
    type: true_false
    prompt: "SMRs are defined as small nuclear reactors with a maximum electrical output of 300 MWe."
    points: 1
    answer: true

  - id: final-quiz2
    type: true_false
    prompt: "A key economic feature of SMRs is modular factory assembly."
    points: 1
    answer: true

  - id: final-quiz3
    type: true_false
    prompt: "Passive safety in SMRs can rely on natural circulation to cool the reactor core."
    points: 1
    answer: true

  - id: final-quiz4
    type: true_false
    prompt: "The European SMR Industrial Alliance was launched in February 2024."
    points: 1
    answer: true
```

<!-- Course contents End -->
