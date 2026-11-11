# Playing Nine Men's Morris (Mill)

Version: **Python 3.13**

## Setup
 
Open a terminal in the project folder `mill/` and create a virtual environment.
 
**Windows**
```
py -3.13 -m venv .venv
.venv\Scripts\Activate.ps1
```

**Linux / macOS**
```
python3.13 -m venv .venv
source .venv/bin/activate
```

Then install the packages inside the environment:

```
python -m pip install --upgrade pip
python -m pip install numpy gymnasium pettingzoo pygame progress imageio-ffmpeg
```

## Experiments

**1. UCT influence**
```
python -m src.bin.uct_influence --iterations 100 --games 20 --seed 1
```

**2. Difficulties competition**
```
python -m src.bin.difficulty_competition --games 10 --seed 1
```

**3. Computation time**
```
python -m src.bin.difficulty_computation --iterations 15 350 750 1500 --positions 10 --seed 1
```

**4. Human vs AI** (use `--side 2` to play second)
```
python -m src.bin.human_vs_ai --difficulty peaceful --side 1 --seed 1
python -m src.bin.human_vs_ai --difficulty easy --side 1 --seed 1
python -m src.bin.human_vs_ai --difficulty medium --side 1 --seed 1
python -m src.bin.human_vs_ai --difficulty hard --side 1 --seed 1
python -m src.bin.human_vs_ai --difficulty insanity --side 1 --seed 1
```