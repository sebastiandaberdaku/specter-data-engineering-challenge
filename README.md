# specter-data-engineering-challenge
## The Specter Data Engineering Challenge! 

This package contains [my](https://sebastiandaberdaku.github.io/resume) solutions to this challenge.

The challenge specification is available [here](Specter%20-%20Senior%20Data%20Engineer%20Challenge.pdf).

The following commands will set up a conda environment and install the requirements.
```shell
conda create --name specter --yes python=3.11 
conda activate specter
pip install -r requirements.txt
```

Run the analysis with the following command:
```shell
python src/main.py
```

Run the tests with the following command:
```shell
pytest src/ 
```

The answers to the questions of the second part of challenge are available [here](answers_to_challenge_questions.md).