create table
    if not exists newses(
        `id` bigint not null PRIMARY KEY,
        `news_id` BIGINT not null,
        `title` varchar(200) not null,
        `date` timestamp not null,
        `url` varchar(400) not null,
        `scraped_at` timestamp not null,
        INDEX idx_news_id (news_id)
    );

CREATE TABLE
    IF NOT EXISTS contents(
        `id` BIGINT,
        FOREIGN KEY (id) REFERENCES newses(news_id),
        `content` VARCHAR(2000) NOT NULL
    )