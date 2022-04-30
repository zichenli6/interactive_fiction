# Interactive Fiction


## 1. Virtual Environment Set Up
Set up virtual environment with either Anaconda or Python venv (optional but recommended)

## 2. Install Libraries

    python3 -m pip install -r requirements.txt

## 3. Download DialoGPT Model
Save the fine-tuned model([download here](https://drive.google.com/file/d/1cB_KhDmArnk-FRNJUtPDt21WgSDAOYfr/view?usp=sharing)) to "game/static/game/dialoGPT.pth"

## 4. Make Django Migrations

    python manage.py makemigrations
    python manage.py migrate

## 5. Start Django Web App
Open terminal, activate virtual environment, and run

    python manage.py runserver

## 6. Play
Open your favorite browser and go to the local url provided by the terminal in step 5.
