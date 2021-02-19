create table if not exists migrations
(
    version    text primary key,
    applied_at timestamp not null default statement_timestamp()
);
