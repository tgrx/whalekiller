create table tag
(
    tag_pk serial primary key,
    name   text not null unique
);
