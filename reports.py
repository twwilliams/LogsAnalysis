#!/usr/bin/env python3

"""
Reporting module for news article system that answers three questions:

(1) What are the most popular three articles of all time?
(2) Who are the most popular article authors of all time?
(3) On which days did more than 1% of requests lead to errors?
"""

import psycopg2

DATABASE = 'news'


def popular_articles(count=3):
    return """
        SELECT COUNT(log.status) as views, articles.title
            FROM articles, log
            WHERE log.path = '/article/' || articles.slug
            GROUP BY articles.title
            ORDER BY views DESC
            LIMIT {};
    """.format(count)


def popular_authors():
    return """
        SELECT COUNT(log.id), authors.name FROM articles, authors, log
        WHERE (log.path = '/article/' || articles.slug)
          AND (articles.author = authors.id)
        GROUP BY authors.name
        ORDER BY COUNT(log.id) DESC;"""


def high_error_days(limit=1):
    return """
        SELECT successes_per_day.success_count AS successes,
          errors_per_day.error_count AS errors,
          successes_per_day.date AS date,
          Round((errors_per_day.error_count::numeric /
                (errors_per_day.error_count +
                 successes_per_day.success_count) * 100),2)
            AS error_percent
        FROM successes_per_day, errors_per_day
        WHERE successes_per_day.date = errors_per_day.date
          AND (errors_per_day.error_count::numeric /
              (errors_per_day.error_count +
               successes_per_day.success_count) * 100) >= {}
        ORDER BY date;
    """.format(limit)


def run_query(query):
    with psycopg2.connect(database=DATABASE) as db:
        c = db.cursor()
        c.execute(query)
        return c.fetchall()


if __name__ == '__main__':
    print("Most popular articles")
    print(run_query(popular_articles(count=3)))

    print()

    print("Most popular authors")
    print(run_query(popular_authors()))

    print()

    print("Days with error rate greater than 1%")
    print(run_query(high_error_days(limit=1)))
