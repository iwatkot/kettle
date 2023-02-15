## Overview
This project is designed to create a simple abstract model of a kettle and visualize it both in command line and on a webpage.<br>
Example of the class `Kettle` initiates with specifications from `TOML` config file and an amount of water, which will be provided by user.<br>
For easy access to config parameters without any string-like syntax, the project uses `Pydantic` model.<br>
The Flask webpages using simple base template with bootstrap4 CSS.<br>

## Features
1. Custom logger class (based on Python's logging module) is designed to write logs to a file. The name of the log file generates with a current date. The logger doesn't use stdout.<br>
2. In addition to logger all messages are writing into SQLite database with simple function in database_handler.<br>
3. User can interact with the kettle example in command line using the `poetry run start` command.<br>
4. Also user can interact with the kettle example on webpage `/kettle/new`. It allows to create a new kettle and turn it on or off.<br>

## Flask webpage example
![Flask web page example](https://touringcrew.com/img_share/kettle_flask.gif)


## ASCIInema examples
1. **Creating a kettle and turning it off while heating.**<br>
[![asciicast](https://asciinema.org/a/7M2nSfxwrVPFa4r0b6YotQbaE.svg)](https://asciinema.org/a/7M2nSfxwrVPFa4r0b6YotQbaE)
<br>

2. **Creating an empty kettle and turning it on.**<br>
[![asciicast](https://asciinema.org/a/Lw3NCKGNrDhJQg2QFrSZzCtRQ.svg)](https://asciinema.org/a/Lw3NCKGNrDhJQg2QFrSZzCtRQ)
<br>

3. **Creating a kettle and not turning it on.**<br>
[![asciicast](https://asciinema.org/a/pLmPDsTnX7akFfmzClqrvHvsF.svg)](https://asciinema.org/a/pLmPDsTnX7akFfmzClqrvHvsF)
<br>

4. **Creating a kettle, turning it on and wait till the water boils.**<br>
[![asciicast](https://asciinema.org/a/ezJjGJcrXiDjDAcXnxh8qimcd.svg)](https://asciinema.org/a/ezJjGJcrXiDjDAcXnxh8qimcd)