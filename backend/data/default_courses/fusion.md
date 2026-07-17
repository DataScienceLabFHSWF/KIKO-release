---
schema: course.v1

course:
  id: nuclear-fusion-the-energy-of-the-future
  source_doc: "fusion.md"
  title: "Nuclear Fusion: The Energy of the Future"
  version: "2.1"
  provider: "Course Team"
  language: English
  level: Beginner
  tags: [fusion, physics, plasma, tokamak, energy, nuclear-fusion]
  estimated_minutes: 45
  published: true
  prerequisites: []

instructors:
  - id: inst-1
    name: "Course Team"
    bio: "Introductory course on nuclear fusion, plasma physics, and Tokamak-based magnetic confinement."

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
    title: "FuseNet - The European Fusion Education Network"
    type: link
    url: "https://fusenet.eu/"
  - id: res-2
    title: "ITER - The Way to New Energy"
    type: link
    url: "https://www.iter.org/"
  - id: res-3
    title: "EUROfusion"
    type: link
    url: "https://euro-fusion.org/"
---

<!-- Course contents start -->

# Nuclear Fusion: The Energy of the Future

## Course overview

This course introduces the global energy challenge and explains why nuclear fusion is considered a promising long-term energy source. It then covers the basic fusion reaction, the nature of plasma, and how Tokamak devices use magnetic fields to confine super-heated fuel.

### Learning outcomes

- Explain the global energy problem and why fusion is considered a potential solution.
- Describe the principles of nuclear fusion and the Deuterium-Tritium reaction.
- Define plasma and explain its key properties.
- Understand how a Tokamak confines plasma using magnetic fields.

## Modules

### Module 1: The Energy Problem and Why Fusion Matters {#m1}

#### Content

##### The Energy Problem

The world is facing a significant energy problem driven by three main factors. First, the world population is increasing and is expected to reach 9.7 billion by 2050. Second, the average energy use per person is rising as countries develop and standards of living improve. Finally, most energy still comes from fossil fuels, which cause greenhouse gas emissions leading to climate change.

While solar and wind are growing, they are intermittent (they do not run nonstop) and require energy storage. Nuclear fusion offers a potential solution: it is sustainable, inherently safe, produces no carbon emissions, and uses abundant fuel.

#### Questions (practice / free-response)

```yaml
- id: m1-q1
  prompt: "What are the three main factors described as driving the global energy problem?"
  reference_answer: "The three factors are population growth, rising energy use per person, and the continued dominance of fossil fuels that drive greenhouse gas emissions and climate change."
  points: 1

- id: m1-q2
  prompt: "Why is fusion presented as a potential solution to the energy problem?"
  reference_answer: "Fusion is presented as a potential solution because it is sustainable, inherently safe, produces no carbon emissions, and uses abundant fuel."
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
    prompt: "Which of the following is identified as part of the global energy problem?"
    points: 1
    choices:
      - id: a1
        text: "Most energy still comes from fossil fuels."
        correct: true
        feedback: "Correct. The lesson identifies continued reliance on fossil fuels as a key part of the energy problem."
      - id: a2
        text: "Global energy demand is steadily disappearing."
        correct: false
        feedback: "Incorrect. The lesson says energy use per person is rising, not disappearing."
      - id: a3
        text: "Population is expected to shrink dramatically by 2050."
        correct: false
        feedback: "Incorrect. The lesson states that world population is expected to increase."

  - id: m1-quiz2
    type: mcq
    prompt: "Why is fusion described as a promising energy source?"
    points: 1
    choices:
      - id: a1
        text: "Because it is sustainable, inherently safe, and produces no carbon emissions."
        correct: true
        feedback: "Correct. Those are the main advantages highlighted in the lesson."
      - id: a2
        text: "Because it depends entirely on burning fossil fuels more efficiently."
        correct: false
        feedback: "Incorrect. Fusion is presented as an alternative to fossil-fuel dependence."
      - id: a3
        text: "Because it removes the need for all other energy sources today."
        correct: false
        feedback: "Incorrect. The lesson presents fusion as a potential solution, not as an immediate total replacement."
```

#### Further reading

- [FuseNet - The European Fusion Education Network](https://fusenet.eu/)
- [ITER - The Way to New Energy](https://www.iter.org/)

#### Common misconceptions

```yaml
- misconception: "Fusion solves the energy problem simply because demand is falling."
  correction: "The lesson states the opposite: population and energy use per person are rising, which increases pressure on energy systems."

- misconception: "Fusion is mainly proposed because renewables never work."
  correction: "The lesson says solar and wind are growing, but they are intermittent and require storage. Fusion is presented as an additional potential solution."
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

### Module 2: What is Nuclear Fusion? {#m2}

#### Content

##### What is Nuclear Fusion?

Nuclear fusion is the process that powers the Sun. In the core of the Sun, gravity creates extreme pressure and temperature, forcing particles to fuse together.

![Deuterium-Tritium reaction releasing massive energy and neutrons.](/api/course/{{COURSE_ID}}/images/Fusion_course_1_atoms.png)

On Earth, the most accessible fusion reaction is **D-T fusion** (Deuterium-Tritium). In this reaction:

- **Deuterium** (hydrogen with one neutron) and **Tritium** (hydrogen with two neutrons) fuse.
- They form a **Helium** nucleus and a free **neutron**.
- This releases a massive amount of energy: 17.6 MeV.

The energy density of fusion is incredibly high; fusing one liter of D-T fuel produces about 10 million times more energy than burning one liter of gasoline.

#### Questions (practice / free-response)

```yaml
- id: m2-q1
  prompt: "Which two hydrogen isotopes are used in the primary fusion reaction described in the course?"
  reference_answer: "The reaction uses Deuterium and Tritium."
  points: 1

- id: m2-q2
  prompt: "What are the products of the Deuterium-Tritium fusion reaction?"
  reference_answer: "The reaction produces a Helium nucleus and a free neutron, releasing 17.6 MeV of energy."
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
    prompt: "Which two isotopes of hydrogen are used in the primary fusion reaction described?"
    points: 1
    choices:
      - id: a1
        text: "Hydrogen and Helium"
        correct: false
        feedback: "Incorrect. Helium is the result of the reaction, not the fuel."
      - id: a2
        text: "Deuterium and Tritium"
        correct: true
        feedback: "Correct. Deuterium and Tritium are the most accessible fusion fuel mix described in the lesson."
      - id: a3
        text: "Uranium and Plutonium"
        correct: false
        feedback: "Incorrect. Those are associated with fission, not the fusion reaction described here."

  - id: m2-quiz2
    type: mcq
    prompt: "What does the D-T fusion reaction produce?"
    points: 1
    choices:
      - id: a1
        text: "A Helium nucleus and a free neutron"
        correct: true
        feedback: "Correct. Those are the reaction products identified in the course."
      - id: a2
        text: "Only two free electrons"
        correct: false
        feedback: "Incorrect. That is not the reaction product described."
      - id: a3
        text: "A Uranium nucleus"
        correct: false
        feedback: "Incorrect. Uranium is not produced in the D-T fusion reaction."
```

#### Further reading

- [ITER - The Way to New Energy](https://www.iter.org/)
- [EUROfusion](https://euro-fusion.org/)

#### Common misconceptions

```yaml
- misconception: "Fusion and fission use the same type of fuel."
  correction: "The lesson explains that the main fusion reaction here uses Deuterium and Tritium, not heavy fission fuels such as uranium or plutonium."

- misconception: "Fusion only produces small amounts of energy."
  correction: "The lesson states that D-T fusion releases 17.6 MeV per reaction and has a very high energy density."
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

### Module 3: Plasma - The Fourth State of Matter {#m3}

#### Content

##### Plasma: The Fourth State of Matter

To achieve fusion on Earth, we must heat the fuel to extreme temperatures. When a gas is heated beyond a certain threshold, it undergoes **ionization**. The electrons are stripped from the nuclei, creating a mixture of free ions and electrons called a **plasma**.

![Plasma: The high-energy, ionized fourth state of matter.](/api/course/{{COURSE_ID}}/images/Fusion_course_2_states.jpg)

Plasma is often called the fourth state of matter. Unlike a neutral gas, a plasma conducts electricity and can be controlled by electric and magnetic fields.

#### Questions (practice / free-response)

```yaml
- id: m3-q1
  prompt: "What happens to a gas when it is heated enough to become a plasma?"
  reference_answer: "It becomes ionized: electrons are stripped from the nuclei, producing free ions and free electrons."
  points: 1

- id: m3-q2
  prompt: "Why can plasma be controlled by magnetic fields?"
  reference_answer: "Because plasma is an ionized gas containing charged particles, it conducts electricity and responds to electric and magnetic fields."
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
    prompt: "What defines a plasma?"
    points: 1
    choices:
      - id: a1
        text: "A gas that has been frozen to absolute zero."
        correct: false
        feedback: "Incorrect. Plasma is created by heating, not freezing."
      - id: a2
        text: "An ionized gas consisting of free positive ions and free electrons."
        correct: true
        feedback: "Correct. That is the definition given in the lesson."
      - id: a3
        text: "A liquid metal used to transfer heat."
        correct: false
        feedback: "Incorrect. Plasma is a distinct state of matter."

  - id: m3-quiz2
    type: mcq
    prompt: "Which property of plasma is emphasized in the course?"
    points: 1
    choices:
      - id: a1
        text: "It conducts electricity and can be controlled by electric and magnetic fields."
        correct: true
        feedback: "Correct. The lesson highlights this as a key feature of plasma."
      - id: a2
        text: "It is chemically inert and unaffected by magnetic fields."
        correct: false
        feedback: "Incorrect. Plasma is specifically described as controllable by electric and magnetic fields."
      - id: a3
        text: "It is always cooler than an ordinary gas."
        correct: false
        feedback: "Incorrect. Plasma is formed at very high temperatures."
```

#### Further reading

- [FuseNet - The European Fusion Education Network](https://fusenet.eu/)
- [EUROfusion](https://euro-fusion.org/)

#### Common misconceptions

```yaml
- misconception: "Plasma is just an ordinary hot gas with no major differences."
  correction: "The lesson explains that plasma is ionized, conducts electricity, and can be controlled by electric and magnetic fields."

- misconception: "Plasma is a solid or liquid fuel form."
  correction: "Plasma is described as the fourth state of matter, made of free ions and electrons."
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

### Module 4: Confining the Plasma - The Tokamak {#m4}

#### Content

##### Confining the Plasma: The Tokamak

Since we cannot use gravity to confine the hot plasma like the Sun does, we use **Magnetic Confinement Fusion (MCF)**. The most common device for this is the **Tokamak**, a Russian acronym for "Toroidal chamber with magnetic coils".

![Magnetic fields confining super-heated plasma inside a Tokamak.](/api/course/{{COURSE_ID}}/images/Fusion_course_3_tokamak.gif)

The Tokamak is a doughnut-shaped (toroidal) vacuum chamber surrounded by magnets.

1. **Toroidal Field Coils:** Large D-shaped magnets wrapped around the chamber create the primary magnetic field to guide particles around the torus.
2. **Central Solenoid:** Located in the center, it acts as a transformer to induce a current inside the plasma itself.
3. **Poloidal Field:** The current in the plasma generates a second magnetic field (poloidal), which twists the magnetic field lines into a helical shape, stabilizing the plasma.

This magnetic cage keeps the super-hot plasma away from the walls, allowing fusion to occur without melting the device.

#### Questions (practice / free-response)

```yaml
- id: m4-q1
  prompt: "Why is magnetic confinement needed in a Tokamak?"
  reference_answer: "Magnetic confinement is needed because the plasma is extremely hot and cannot be allowed to touch the reactor walls."
  points: 1

- id: m4-q2
  prompt: "What are the three main magnet systems described in the Tokamak lesson, and what do they do?"
  reference_answer: "The Toroidal Field Coils create the main magnetic field around the torus, the Central Solenoid induces current in the plasma, and the Poloidal Field helps twist and stabilize the magnetic field lines around the plasma."
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
    prompt: "Why is a magnetic field used in a Tokamak?"
    points: 1
    choices:
      - id: a1
        text: "To confine the plasma and keep it away from the reactor walls."
        correct: true
        feedback: "Correct. No material can withstand the heat of fusion plasma, so magnetic fields keep it suspended away from the walls."
      - id: a2
        text: "To convert the heat directly into electricity."
        correct: false
        feedback: "Incorrect. The magnetic field is used for confinement, not direct electrical conversion."
      - id: a3
        text: "To cool down the plasma to a solid state."
        correct: false
        feedback: "Incorrect. Fusion requires extremely hot plasma, not cooling it to a solid."

  - id: m4-quiz2
    type: mcq
    prompt: "What does the central solenoid do in a Tokamak?"
    points: 1
    choices:
      - id: a1
        text: "It induces a current inside the plasma."
        correct: true
        feedback: "Correct. The central solenoid acts as a transformer to drive current in the plasma."
      - id: a2
        text: "It stores all fusion fuel outside the chamber."
        correct: false
        feedback: "Incorrect. That is not its role in the lesson."
      - id: a3
        text: "It removes the need for all other magnetic fields."
        correct: false
        feedback: "Incorrect. Tokamak confinement uses multiple magnetic field systems."
```

#### Further reading

- [ITER - The Way to New Energy](https://www.iter.org/)
- [EUROfusion](https://euro-fusion.org/)

#### Common misconceptions

```yaml
- misconception: "A Tokamak works like the Sun by using gravity to confine fusion fuel."
  correction: "The lesson explains that, unlike the Sun, a Tokamak uses magnetic confinement because gravity cannot be used on Earth in the same way."

- misconception: "The plasma can safely touch the reactor walls during operation."
  correction: "The lesson states that magnetic confinement keeps the plasma away from the walls because the plasma is extremely hot."
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
    prompt: "Fusion is presented in the course as a potential response to rising energy demand and climate change."
    points: 1
    answer: true

  - id: final-quiz2
    type: true_false
    prompt: "The primary fusion reaction described in the course uses Deuterium and Tritium."
    points: 1
    answer: true

  - id: final-quiz3
    type: true_false
    prompt: "Plasma is an ionized gas made of free ions and electrons."
    points: 1
    answer: true

  - id: final-quiz4
    type: true_false
    prompt: "A Tokamak uses magnetic fields to keep hot plasma away from the reactor walls."
    points: 1
    answer: true
```

<!-- Course contents End -->
