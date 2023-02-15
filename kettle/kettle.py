import prompt
import threading
import uuid

from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap4
from pydantic import BaseSettings
from enum import Enum
from time import sleep

from log_handler import Logger
from database_handler import execute_query

logger = Logger(__name__)
app = Flask(__name__)
bootstrap = Bootstrap4(app)


class KettleConfig(BaseSettings):
    """Loads kettle configuration from TOML file."""
    manufacturer: str
    model: str
    volume: float
    color: str
    power: int
    voltage: int
    wire_len: float
    warranty: int

    class Config:
        env_file = "pyproject.toml"
        env_file_encoding = "utf-8"


class Constants(Enum):
    """Stores constants for the module."""
    minimum_water_amount = 0.0
    maximum_water_amount = 1.0
    room_temerature = 20
    boiling_time = 10
    boiling_temperature = 100


class LogTemplates(Enum):
    """Stores templates for the logger."""
    started = "The script has started."
    init = "The kettle was initiated with {}L water."
    incorrect_water_inpit = "Incorrect amount of water was entered by user."
    switcher_used = "The switcher was used by the user, while the kettle "\
        "in status {}."
    turned_off = "The kettle is now turned OFF. Status: {}."
    turned_on = "The kettle is now turned ON. Status: {}."
    broken = "The kettle was broken by the user, because was turned on "\
        "without water."
    heating_started = "The heating of the kettle has been started. Initial "\
        "temperature: {}C. Temperature delta: {}C. Boiling speed: {}C/s."
    heated = "The water in the kettle was successfully boiled to the boiling "\
        "temperature of {}C."
    interrupted = "The heating proccess was interrupted by the user."
    exiting = "The scripts is exiting now."


class Messages(Enum):
    """Stores message templates for the module."""
    welcome = "Hi there! You can control your virtual kettle with this "\
        "script."
    water_amount_input = "Please enter float water amount between {minimum} "\
        "and {maximum}. This is a required value.\nAmount of water: "
    turnon_input = "To turn on the kettle please enter `on`. Any other "\
        "input will close the program.\nInput: "
    goodbye = "Thank you for using our virtual kettle. Come back soon!"
    kettle_on = "The kettle is now turned ON."
    kettle_off = "The kettle is now turned OFF."
    kettle_broken = "You turned on the kettle without any water and broke it."\
        "\nWhy did you do it?"
    wrong_water_amount = "The wrong amount of water was entered. Please "\
        "try again."
    kettle_heating = "The kettle is heating now, current temperature: {}C. "\
        "To stop the heating process press Ctrl+C."
    kettle_auto_off = "The kettle was turned off automatically after "\
        "the water reached boiling temperature."
    repr_template = "It's a {color} kettle {manufacturer} {model}. It has "\
        "{volume}L volume, the power of {power}W with {voltage}V voltage "\
        "and a wire with lenght of {wire_len}M. The manufacturer provides "\
        "{warranty} month warranty."
    kettle_created = "You successfully created the kettle."


class FlaskMessages(Enum):
    """Stores the Flask messages."""
    wrong_volume = "Please enter a valid number for the water amount!"


class Kettle:
    """Creates the kettle object with specified water amount."""
    def __init__(self, water_amount: float) -> None:
        logger.debug(LogTemplates.init.value.format(water_amount))
        self.water_amount = water_amount
        # Reading the kettle's parameters from config file.
        self.config = KettleConfig()
        self.status = -1
        # Assuming that water in kettle has the same temperature as air
        # in the room.
        self.temperature = Constants.room_temerature.value
        # Generating short version of UUID for kettle example to easily
        # identify it.
        self.id = str(uuid.uuid4())[:5]
        # By default we have a brand new and cool kettle.
        self.broken = False

    def __repr__(self) -> str:
        return Messages.repr_template.value.format(**self.config.__dict__)

    def switch_status(self) -> None:
        """Handles switching kettle's status and launches boiling if the
        kettle is turned on."""
        logger.debug(LogTemplates.switcher_used.value.format(self.status))
        self.status *= -1
        # If the status is ON(1), launching the boiling process.
        if self.status == 1:
            logger.debug(LogTemplates.turned_on.value.format(self.status))
            print_and_save_to_db(Messages.kettle_on.value)
            self.heating()
        elif self.status == -1:
            logger.debug(LogTemplates.turned_off.value.format(self.status))
            print_and_save_to_db(Messages.kettle_off.value)

    def heating(self) -> None:
        """Handles kettle's heating and switching off (auto or manual)."""
        if self.water_amount == 0:
            logger.debug(LogTemplates.broken.value)
            print_and_save_to_db(Messages.kettle_broken.value)
            # If the kettle was turned on without any water it will broke.
            self.broken = True
            return
        # Couting the temperature difference and the speed of boiling.
        temperature_difference = (Constants.boiling_temperature.value
                                  - self.temperature)
        boiling_speed = temperature_difference // Constants.boiling_time.value

        logger.info(LogTemplates.heating_started.value.format(
            self.temperature, temperature_difference, boiling_speed))

        try:
            while self.temperature < Constants.boiling_temperature.value:
                print_and_save_to_db(Messages.kettle_heating.value.format(
                    self.temperature))
                # Raising the water temperature with a boiling_speed per step.
                self.temperature += boiling_speed
                sleep(1)

            print_and_save_to_db(Messages.kettle_auto_off.value)

            logger.info(LogTemplates.heated.value.format(
                Constants.boiling_temperature.value))
            # When the temperature >= boiling turning the kettle off.
            self.switch_status()
        except KeyboardInterrupt:
            # To stop the cycle, using KeyboardInterrupt.
            logger.info(LogTemplates.interrupted.value)
            self.switch_status()


def print_and_save_to_db(message: str) -> None:
    """Prints the messages and saves it into the database."""
    print(message)
    execute_query(message=message)


def start() -> None:
    """Creates the kettle based on user's input and handles the boiling
    process."""
    # Creates table in the database.
    execute_query()

    logger.info(LogTemplates.started.value)
    print_and_save_to_db(Messages.welcome.value)

    sleep(1)
    water_check = True
    while water_check:
        water_amount = prompt.real(Messages.water_amount_input.value.format(
            minimum=Constants.minimum_water_amount.value,
            maximum=Constants.maximum_water_amount.value))
        if (Constants.minimum_water_amount.value <= water_amount
                <= Constants.maximum_water_amount.value):
            water_check = False
        else:
            logger.warning(LogTemplates.incorrect_water_inpit.value)
            print_and_save_to_db(Messages.wrong_water_amount.value)
    kettle = Kettle(water_amount)
    print_and_save_to_db(Messages.kettle_created.value)
    sleep(1)
    print_and_save_to_db(repr(kettle))
    sleep(1)
    action = input(Messages.turnon_input.value)
    if action == 'on':
        kettle.switch_status()
    print_and_save_to_db(Messages.goodbye.value)
    sleep(1)
    logger.info(LogTemplates.exiting.value)


@app.route('/kettle/new', methods=['GET', 'POST'])
def new_kettle():
    """Handles the webpage, where user can create a new kettle."""
    # Creating global dictionary with examples of kettle class.
    global kettles
    kettles = {}
    # Creating local variables just for shorter code in if statement.
    min_volume = Constants.minimum_water_amount.value
    max_volume = Constants.maximum_water_amount.value
    if request.method == 'POST':
        try:
            # Checking if the entered value is correct.
            water_amount = float(request.form['water_amount'])
            if water_amount < min_volume or water_amount > max_volume:
                raise ValueError(FlaskMessages.wrong_volume.value)
        except (ValueError, TypeError):
            # If the value is incorrect, redirecting to the same page
            # and providing error message as argument.
            return redirect(url_for(
                'new_kettle', error=FlaskMessages.wrong_volume.value))
        kettle = Kettle(water_amount=water_amount)
        # Adding a kettle new example to the global kettle dict.
        kettles[kettle.id] = kettle
        return redirect(url_for('kettle', kettle_id=kettle.id))
    # Reading arguments from the path to create an error message.
    error = request.args.get('error', '')
    return render_template('new_kettle.html', error=error,
                           minimum_water_amount=min_volume,
                           maximum_water_amount=max_volume)


@app.route('/kettle/<kettle_id>/', methods=['GET', 'POST'])
def kettle(kettle_id: str):
    """Handles the webpage, where user can work with created kettle."""
    # Getting the example of kettle by it's UUID (shortened).
    kettle = kettles.get(kettle_id)
    if request.method == 'POST':
        if request.form['switch_status'] == 'Turn On':
            # Turning the kettle ON if the ON button was pressed.
            heating_thread = threading.Thread(target=kettle.switch_status)
            heating_thread.start()
        elif request.form['switch_status'] == 'Turn Off':
            # Turning the kettle OFF if the OFF button was pressed.
            kettle.switch_status()
        return redirect(url_for('kettle', kettle_id=kettle.id))
    return render_template(
        'kettle.html', kettle=kettle,
        boiling_temperature=Constants.boiling_temperature.value)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
