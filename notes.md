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
SELECT articles.title, COUNT(log.status) as views
    FROM articles, log
    WHERE log.path = '/article/' || articles.slug
    GROUP BY articles.title
    ORDER BY views DESC
    LIMIT 3;
```

### 2. Who are the most popular article authors of all time?

authors.id => articles.author
articles.slug => log.path

```
SELECT count(log.id), authors.name FROM articles, authors, log
WHERE (log.path = '/article/' || articles.slug)
    AND (articles.author = authors.id)
GROUP BY authors.name
ORDER BY count(log.id) DESC;
```

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
        (errors_per_day.error_count + successes_per_day.success_count) * 100),2)
            AS error_percent
    FROM successes_per_day, errors_per_day
    WHERE successes_per_day.date = errors_per_day.date
      AND (errors_per_day.error_count::numeric /
           (errors_per_day.error_count + successes_per_day.success_count) * 100) >= 1
    ORDER BY date;
```
