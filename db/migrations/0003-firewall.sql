create table fw
(
    fw_pk      serial primary key,
    fw_id      text    not null unique,
    source_tag integer not null references tag (tag_pk) on update cascade on delete restrict,
    dest_tag   integer not null references tag (tag_pk) on update cascade on delete restrict
);

create index on fw (source_tag);

create index on fw (dest_tag);
