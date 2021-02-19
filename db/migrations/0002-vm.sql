create table vm
(
    vm_pk serial primary key,
    vm_id text not null unique,
    name  text
);


create table vm_tag
(
    vm_pk  integer not null references vm (vm_pk) on update cascade on delete cascade,
    tag_pk integer not null references tag (tag_pk) on update cascade on delete cascade,
    unique (vm_pk, tag_pk)
);

create index on vm_tag (vm_pk);

create index on vm_tag (tag_pk);
