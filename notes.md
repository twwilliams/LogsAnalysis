# Notes

## Database structure

```
news=> \dt
          List of relations
 Schema |   Name   | Type  |  Owner
--------+----------+-------+---------
 public | articles | table | vagrant
 public | authors  | table | vagrant
 public | log      | table | vagrant

news=> \d articles
                                  Table "public.articles"
 Column |           Type           |             Modifiers
--------+--------------------------+-------------------------------------
 author | integer                  | not null
 title  | text                     | not null
 slug   | text                     | not null
 lead   | text                     |
 body   | text                     |
 time   | timestamp with time zone | default now()
 id     | integer                  | not null default
                                     nextval('articles_id_seq'::regclass)

Indexes:
    "articles_pkey" PRIMARY KEY, btree (id)
    "articles_slug_key" UNIQUE CONSTRAINT, btree (slug)
Foreign-key constraints:
    "articles_author_fkey" FOREIGN KEY (author) REFERENCES authors(id)

news=> \d authors
                         Table "public.authors"
 Column |  Type   |                      Modifiers
--------+---------+------------------------------------------------------
 name   | text    | not null
 bio    | text    |
 id     | integer | not null default nextval('authors_id_seq'::regclass)
Indexes:
    "authors_pkey" PRIMARY KEY, btree (id)
Referenced by:
    TABLE "articles"
    CONSTRAINT "articles_author_fkey"
    FOREIGN KEY (author)
    REFERENCES authors(id)

news=> \d log
                            Table "public.log"
 Column |           Type           |         Modifiers
--------+--------------------------+-------------------------------
 path   | text                     |
 ip     | inet                     |
 method | text                     |
 status | text                     |
 time   | timestamp with time zone | default now()
 id     | integer                  | not null default
                                     nextval('log_id_seq'::regclass)
Indexes:
    "log_pkey" PRIMARY KEY, btree (id)

news=> select count(*) from articles;
 count
-------
     8
(1 row)

news=> select count(*) from authors;
 count
-------
     4
(1 row)

news=> select count(*) from log;
  count
---------
 1677735
(1 row)
```
## Questions

### 1. What are the most popular three articles of all time?

```
news=>
SELECT articles.title, COUNT(log.status) as views
FROM articles, log
WHERE log.path = '/article/' || articles.slug
GROUP BY articles.title
ORDER BY views DESC
LIMIT 3;
              title               | views
----------------------------------+--------
 Candidate is jerk, alleges rival | 338647
 Bears love berries, alleges bear | 253801
 Bad things gone, say good people | 170098
(3 rows)
```

### 2. Who are the most popular article authors of all time?

### 3. On which days did more than 1% of requests lead to errors?

There are only two status types: 200 OK and 404 NOT FOUND:
```
news=> SELECT Count(*),status FROM log GROUP BY status;
  count  |    status
---------+---------------
   12908 | 404 NOT FOUND
 1664827 | 200 OK
(2 rows)
```

Looks like we have data for the month of July 2016:
```
news=> SELECT Count(*),time::date FROM log GROUP BY time::date;
 count |    time
-------+------------
 38705 | 2016-07-01
 55200 | 2016-07-02
 54866 | 2016-07-03
 54903 | 2016-07-04
 54585 | 2016-07-05
 54774 | 2016-07-06
 54740 | 2016-07-07
 55084 | 2016-07-08
 55236 | 2016-07-09
 54489 | 2016-07-10
 54497 | 2016-07-11
 54839 | 2016-07-12
 55180 | 2016-07-13
 55196 | 2016-07-14
 54962 | 2016-07-15
 54498 | 2016-07-16
 55907 | 2016-07-17
 55589 | 2016-07-18
 55341 | 2016-07-19
 54557 | 2016-07-20
 55241 | 2016-07-21
 55206 | 2016-07-22
 54894 | 2016-07-23
 55100 | 2016-07-24
 54613 | 2016-07-25
 54378 | 2016-07-26
 54489 | 2016-07-27
 54797 | 2016-07-28
 54951 | 2016-07-29
 55073 | 2016-07-30
 45845 | 2016-07-31
(31 rows)
```

This gets all the data for the errors:
```
SELECT Count(*),status,time::date
FROM log
GROUP BY time::date,status
ORDER BY time::date;
```

Create two views:
```
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

Now, run the query:
```
SELECT successes_per_day.success_count AS successes,
       errors_per_day.error_count AS errors,
       successes_per_day.date AS date,
       ROUND((errors_per_day.error_count::numeric /
        successes_per_day.success_count * 100),2) AS error_percent
    FROM successes_per_day, errors_per_day
    WHERE successes_per_day.date = errors_per_day.date
      AND (errors_per_day.error_count::numeric /
           successes_per_day.success_count * 100) >= 1
    ORDER BY date;
```
