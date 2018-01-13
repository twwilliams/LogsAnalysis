# LogsAnalysis

Logs Analysis project for the Udacity Full Stack Web Developer
Nanodegree program

## Installation

Clone this repository and then copy the file `reports.py` to the Vagrant
image or to a folder that is shared with the Vagrant image.

This tool requires Python 3.5 or later for the code and the Vagrant image
provided by Udacity as part of the "The Backend: Databases & Applications"
section in the curriculum that has PostgreSQL installed and configured
with the **news** database.

You will also need to create two views as described below in the
"Database views" section.

## Database views

Create two views in the database, using the SQL below:

```postgresql
CREATE VIEW errors_per_day as
    SELECT COUNT(*) AS error_count,time::date AS date
    FROM log
    WHERE status LIKE '404%'
    GROUP BY time::date
    ORDER BY time::date;

CREATE VIEW successes_per_day as
    SELECT COUNT(*) AS success_count,time::date AS date
    FROM log
    WHERE status LIKE '200%'
    GROUP BY time::date
    ORDER BY time::date;
```

## Usage

Log into the Vagrant instance, cd to the directory that contains the
script, and run: `python3 reports.py`

## Meta

Tommy Williams | [@twwilliams](https://twitter.com/twwilliams)

Distributed under the MIT license. See `LICENSE` for more information.
