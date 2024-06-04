[GitHub](https://github.com)

# Word Wizard - Multilingual Crossword Game

## Overview

This project is a dynamic and engaging multilingual crossword game designed to empower users with improved language skills. It covers six main European languages and is tailored for L2 learners, with vocabulary divided into 6 CEFR levels (A1, A2, B1, B2, C1, C2).

## Features

- Language and Level Selection: Users can choose a language and a CEFR level that matches their knowledge.
- Dynamic Crossword Generation: Crosswords are generated based on the selected language and level.
- User Authentication: Sign-up and sign-in functionalities for personalized experience.
- Interactive Gameplay: Timed puzzles with scoring and encouraging feedback.

## Setup and Installation

### 1. Set up virtual environment:

`python -m venv env`
`source env/bin/activate`

### 2. Install Dependencies:

`pip install -r requirements.txt`

### 3. Run the Application:

`flask run`

## Usage

- Access the application at localhost:5000.
- Sign up to create a user account.
- Select a language and level to start playing.

## Webpage

The website consists of homepage, registration and login interface and game page.

1. Homepage:

![homepage_design](/Users/ninachen/Desktop/PersonalWebsite/astrofy/public/project_wordwizard/homepage_design.png)

2. Game page

![crossword_design](/Users/ninachen/Desktop/PersonalWebsite/astrofy/public/project_wordwizard/crossword_design.png)

3. Sign-in and sign-up

![sign-in-up](/Users/ninachen/Desktop/PersonalWebsite/astrofy/public/project_wordwizard/sign-in-up.png)

## Technologies

- Backend: Python with Flask
- Frontend: HTML, CSS, JavaScript
- Database: PostgreSQL


## References
[1] CEFRLex: Common European Framework of Reference for Languages (CEFR) scale. <cental.uclouvain.be/cefrlex/ > 
[2] WordNet: A Lexical Database for English. <wordnet.princeton.edu/ >
[3] OMW: Open Multilingual Wordnet. <mwn.org>
[4] https://github.com/jeremy886/crossword_helmig
