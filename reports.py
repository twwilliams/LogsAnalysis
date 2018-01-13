#!/usr/bin/env python3

"""
Reporting module for news article system that answers three questions:

(1) What are the most popular three articles of all time?
(2) Who are the most popular article authors of all time?
(3) On which days did more than 1% of requests lead to errors?

Since this is a simple script, with hard-coded SQL queries, there is no
error-handling. The output formatting might make sense to pull out into a
separate module that could be reused by other scripts like this one.
"""

import psycopg2

DATABASE = 'news'


def popular_articles(count=3):
    """
    Gets the list of the most popular articles
    :param count: The number of articles to return. Default 3.
    :return: The query string
    """
    return """
        SELECT COUNT(log.status) as views, articles.title
            FROM articles, log
            WHERE log.path = '/article/' || articles.slug
            GROUP BY articles.title
            ORDER BY views DESC
            LIMIT {};
    """.format(count)


def popular_authors():
    """
    Gets the list of the most popular authors
    :return: The query string
    """
    return """
        SELECT COUNT(log.id), authors.name FROM articles, authors, log
        WHERE (log.path = '/article/' || articles.slug)
          AND (articles.author = authors.id)
        GROUP BY authors.name
        ORDER BY COUNT(log.id) DESC;"""


def high_error_days(limit=1):
    """
    Gets the list of days with error rates above the limit
    :param limit: The percent threshold for finding a day that has too many
                   errors. Default 1.
    :return: The query string
    """
    return """
        SELECT Round((errors_per_day.error_count::numeric /
                (errors_per_day.error_count +
                 successes_per_day.success_count) * 100),2)
            AS error_percent, successes_per_day.date AS date
        FROM successes_per_day, errors_per_day
        WHERE successes_per_day.date = errors_per_day.date
          AND (errors_per_day.error_count::numeric /
              (errors_per_day.error_count +
               successes_per_day.success_count) * 100) >= {}
        ORDER BY date;
    """.format(limit)


def run_query(query):
    """
    Runs the specified query against the database defined in the DATABASE
    constant
    :param query: The query string to execute
    :return: The results of the query as a list of tuples
    """
    with psycopg2.connect(database=DATABASE) as db:
        c = db.cursor()
        c.execute(query)
        return c.fetchall()


def print_headline(question):
    """
    Prints a headline to the console
    :param question: The question to include in the headline
    """
    print("=" * 50)
    print(question)
    print()


def format_data_table(data, first_col, second_col="Views"):
    """
    Converts a list of tuples into a table suitable for output to the console
    :param data: List of tuples to format
    :param first_col: The name of the first column
    :param second_col: (Optional) The name of the second column
    :return: String suitable to print()
    """
    output = ""
    first_col_width = 1

    # Find the longest first-column entry
    for row in data:
        if len(row[1]) > first_col_width:
            first_col_width = len(row[1])

    for row in data:
        output += format_row(row[1], row[0], first_col_width)

    header = format_row(first_col, second_col, first_col_width)
    header += '-' * len(header)

    return header + '\n' + output


def format_row(column1, column2, column_width=30):
    """
    Formats a row by padding the first column to the specified column_width
    :param column1: The string for the first column
    :param column2: The string for the second column
    :param column_width: The width of the first column
    :return: String with formatted content
    """
    return "{} | {}\n".format(
        (column1 + " " * column_width)[:column_width], column2)


def format_days(days):
    """
    Converts a list of tuples with a date into a list of tuples with a string
    representation of the date
    :param days: List of tuples from database with datetime in second position
    :return: List of tuples as described above
    """
    formatted = []
    for day in days:
        formatted.append((day[0], day[1].strftime('%Y-%m-%d')))
    return formatted


if __name__ == '__main__':
    print_headline("Most popular three articles of all time")
    articles_list = run_query(popular_articles(count=3))
    print(format_data_table(articles_list, "Article name"))

    print_headline("Most popular article authors of all time")
    authors_list = run_query(popular_authors())
    print(format_data_table(authors_list, "Author name"))

    print_headline("Days with more than 1% of requests as errors")
    error_days = format_days(run_query(high_error_days(limit=1)))
    print(format_data_table(error_days, "Day", "Error percent"))
