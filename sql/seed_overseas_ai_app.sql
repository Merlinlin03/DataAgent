CREATE DATABASE IF NOT EXISTS dw2 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS meta2 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE dw2;

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS fact_store_review_daily;
DROP TABLE IF EXISTS fact_app_quality_daily;
DROP TABLE IF EXISTS fact_ad_revenue_daily;
DROP TABLE IF EXISTS fact_subscription_daily;
DROP TABLE IF EXISTS fact_user_activity_daily;
DROP TABLE IF EXISTS dim_product;
DROP TABLE IF EXISTS dim_app_version;
DROP TABLE IF EXISTS dim_channel;
DROP TABLE IF EXISTS dim_country;
DROP TABLE IF EXISTS dim_date;

CREATE TABLE dim_date (
  date_id INT PRIMARY KEY,
  date_value DATE NOT NULL,
  week_of_year INT NOT NULL,
  month VARCHAR(7) NOT NULL,
  quarter VARCHAR(7) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE dim_country (
  country_id INT PRIMARY KEY,
  country_name VARCHAR(64) NOT NULL,
  region VARCHAR(64) NOT NULL,
  primary_language VARCHAR(64) NOT NULL,
  tier VARCHAR(32) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE dim_channel (
  channel_id INT PRIMARY KEY,
  channel_name VARCHAR(64) NOT NULL,
  channel_type VARCHAR(32) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE dim_app_version (
  version_id INT PRIMARY KEY,
  version_name VARCHAR(32) NOT NULL,
  platform VARCHAR(32) NOT NULL,
  release_date DATE NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE dim_product (
  product_id INT PRIMARY KEY,
  product_name VARCHAR(64) NOT NULL,
  product_category VARCHAR(64) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE fact_user_activity_daily (
  activity_id BIGINT PRIMARY KEY,
  date_id INT NOT NULL,
  country_id INT NOT NULL,
  channel_id INT NOT NULL,
  version_id INT NOT NULL,
  product_id INT NOT NULL,
  dau INT NOT NULL,
  new_users INT NOT NULL,
  retained_d1_users INT NOT NULL,
  retained_d7_users INT NOT NULL,
  sessions INT NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE fact_subscription_daily (
  subscription_id BIGINT PRIMARY KEY,
  date_id INT NOT NULL,
  country_id INT NOT NULL,
  channel_id INT NOT NULL,
  version_id INT NOT NULL,
  product_id INT NOT NULL,
  trial_users INT NOT NULL,
  paid_subscribers INT NOT NULL,
  renewed_subscribers INT NOT NULL,
  refunded_subscribers INT NOT NULL,
  subscription_revenue DECIMAL(12,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE fact_ad_revenue_daily (
  ad_id BIGINT PRIMARY KEY,
  date_id INT NOT NULL,
  country_id INT NOT NULL,
  channel_id INT NOT NULL,
  version_id INT NOT NULL,
  product_id INT NOT NULL,
  ad_impressions INT NOT NULL,
  ad_clicks INT NOT NULL,
  ad_revenue DECIMAL(12,2) NOT NULL,
  ecpm DECIMAL(10,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE fact_app_quality_daily (
  quality_id BIGINT PRIMARY KEY,
  date_id INT NOT NULL,
  country_id INT NOT NULL,
  version_id INT NOT NULL,
  product_id INT NOT NULL,
  total_sessions INT NOT NULL,
  crash_sessions INT NOT NULL,
  error_count INT NOT NULL,
  avg_startup_ms INT NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE fact_store_review_daily (
  review_id BIGINT PRIMARY KEY,
  date_id INT NOT NULL,
  country_id INT NOT NULL,
  version_id INT NOT NULL,
  product_id INT NOT NULL,
  review_count INT NOT NULL,
  bad_review_count INT NOT NULL,
  rating_sum DECIMAL(12,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO dim_date (date_id, date_value, week_of_year, month, quarter) VALUES
(20260801, '2026-08-01', 31, '2026-08', '2026-Q3'),
(20260808, '2026-08-08', 32, '2026-08', '2026-Q3'),
(20260815, '2026-08-15', 33, '2026-08', '2026-Q3'),
(20260816, '2026-08-16', 33, '2026-08', '2026-Q3'),
(20260822, '2026-08-22', 34, '2026-08', '2026-Q3'),
(20260826, '2026-08-26', 35, '2026-08', '2026-Q3');

INSERT INTO dim_country (country_id, country_name, region, primary_language, tier) VALUES
(1, 'United States', 'North America', 'English', 'Core'),
(2, 'Germany', 'Europe', 'German', 'Core'),
(3, 'Brazil', 'LATAM', 'Portuguese', 'Growth'),
(4, 'Japan', 'APAC', 'Japanese', 'Core'),
(5, 'India', 'APAC', 'Hindi', 'Growth'),
(6, 'Spain', 'Europe', 'Spanish', 'Growth');

INSERT INTO dim_channel (channel_id, channel_name, channel_type) VALUES
(1, 'TikTok Ads', 'Paid'),
(2, 'Meta Ads', 'Paid'),
(3, 'Google Ads', 'Paid'),
(4, 'Organic', 'Organic'),
(5, 'App Store Search', 'Store Search');

INSERT INTO dim_app_version (version_id, version_name, platform, release_date) VALUES
(1, '3.1.0', 'iOS', '2026-07-20'),
(2, '3.1.0', 'Android', '2026-07-20'),
(3, '3.2.0', 'iOS', '2026-08-15'),
(4, '3.2.0', 'Android', '2026-08-15');

INSERT INTO dim_product (product_id, product_name, product_category) VALUES
(1, 'AI Chat Assistant', 'Chatbot'),
(2, 'AI Image Studio', 'Image Generator'),
(3, 'AI Writing Copilot', 'Writing Assistant');

INSERT INTO fact_user_activity_daily VALUES
(1001, 20260801, 1, 1, 1, 1, 18240, 3260, 1370, 690, 51400),
(1002, 20260808, 1, 1, 1, 1, 19580, 3480, 1510, 760, 55320),
(1003, 20260815, 1, 1, 3, 1, 21460, 3890, 1660, 840, 62780),
(1004, 20260822, 1, 1, 3, 1, 22620, 4020, 1750, 890, 68210),
(1005, 20260826, 1, 1, 3, 1, 23110, 4160, 1810, 940, 70140),
(1006, 20260826, 1, 4, 3, 1, 15420, 1980, 820, 430, 46300),
(1007, 20260826, 2, 3, 3, 2, 8620, 1340, 510, 260, 24110),
(1008, 20260826, 3, 2, 4, 2, 11980, 2410, 890, 420, 32670),
(1009, 20260826, 4, 5, 3, 3, 7340, 960, 410, 210, 19980),
(1010, 20260826, 5, 1, 4, 1, 14120, 3560, 1160, 540, 38950),
(1011, 20260826, 6, 2, 3, 1, 6840, 1180, 420, 190, 18120),
(1012, 20260816, 1, 1, 3, 1, 21880, 3950, 1685, 850, 64200);

INSERT INTO fact_subscription_daily VALUES
(2001, 20260801, 1, 1, 1, 1, 820, 246, 1180, 18, 8820.40),
(2002, 20260808, 1, 1, 1, 1, 910, 292, 1260, 20, 10134.20),
(2003, 20260815, 1, 1, 3, 1, 1080, 360, 1340, 26, 12488.60),
(2004, 20260822, 1, 1, 3, 1, 1160, 402, 1420, 31, 13872.80),
(2005, 20260826, 1, 1, 3, 1, 1210, 438, 1460, 28, 15116.50),
(2006, 20260826, 1, 4, 3, 1, 510, 154, 910, 12, 6420.00),
(2007, 20260826, 2, 3, 3, 2, 380, 109, 420, 9, 3760.30),
(2008, 20260826, 3, 2, 4, 2, 610, 168, 530, 16, 4894.10),
(2009, 20260826, 4, 5, 3, 3, 260, 86, 380, 7, 3028.00),
(2010, 20260826, 5, 1, 4, 1, 840, 182, 510, 22, 3985.70),
(2011, 20260826, 6, 2, 3, 1, 330, 92, 290, 14, 2716.90),
(2012, 20260816, 1, 1, 3, 1, 1095, 365, 1360, 37, 12610.00);

INSERT INTO fact_ad_revenue_daily VALUES
(3001, 20260801, 1, 1, 1, 1, 920000, 38400, 2760.00, 3.00),
(3002, 20260808, 1, 1, 1, 1, 990000, 41200, 3069.00, 3.10),
(3003, 20260815, 1, 1, 3, 1, 1110000, 46300, 3663.00, 3.30),
(3004, 20260822, 1, 1, 3, 1, 1190000, 50200, 4046.00, 3.40),
(3005, 20260826, 1, 1, 3, 1, 1240000, 53100, 4340.00, 3.50),
(3006, 20260826, 1, 4, 3, 1, 610000, 18400, 2013.00, 3.30),
(3007, 20260826, 2, 3, 3, 2, 420000, 12600, 1596.00, 3.80),
(3008, 20260826, 3, 2, 4, 2, 760000, 25300, 1824.00, 2.40),
(3009, 20260826, 4, 5, 3, 3, 280000, 8100, 1176.00, 4.20),
(3010, 20260826, 5, 1, 4, 1, 890000, 29400, 1335.00, 1.50),
(3011, 20260826, 6, 2, 3, 1, 350000, 10200, 980.00, 2.80),
(3012, 20260816, 1, 1, 3, 1, 1135000, 47400, 3859.00, 3.40);

INSERT INTO fact_app_quality_daily VALUES
(4001, 20260801, 1, 1, 1, 51400, 308, 820, 1280),
(4002, 20260808, 1, 1, 1, 55320, 360, 910, 1305),
(4003, 20260815, 1, 3, 1, 62780, 941, 1640, 1510),
(4004, 20260816, 1, 3, 1, 64200, 1124, 1810, 1580),
(4005, 20260822, 1, 3, 1, 68210, 955, 1420, 1460),
(4006, 20260826, 1, 3, 1, 70140, 912, 1370, 1420),
(4007, 20260826, 2, 3, 2, 24110, 217, 410, 1335),
(4008, 20260826, 3, 4, 2, 32670, 425, 770, 1490),
(4009, 20260826, 4, 3, 3, 19980, 180, 350, 1210),
(4010, 20260826, 5, 4, 1, 38950, 584, 940, 1675),
(4011, 20260826, 6, 3, 1, 18120, 290, 520, 1550);

INSERT INTO fact_store_review_daily VALUES
(5001, 20260801, 1, 1, 1, 340, 32, 1510.0),
(5002, 20260808, 1, 1, 1, 372, 39, 1640.0),
(5003, 20260815, 1, 3, 1, 415, 61, 1760.0),
(5004, 20260816, 1, 3, 1, 430, 74, 1792.0),
(5005, 20260822, 1, 3, 1, 468, 56, 2030.0),
(5006, 20260826, 1, 3, 1, 492, 52, 2160.0),
(5007, 20260826, 2, 3, 2, 188, 24, 820.0),
(5008, 20260826, 3, 4, 2, 260, 42, 1050.0),
(5009, 20260826, 4, 3, 3, 144, 12, 655.0),
(5010, 20260826, 5, 4, 1, 310, 58, 1206.0),
(5011, 20260826, 6, 3, 1, 205, 47, 770.0);

SET FOREIGN_KEY_CHECKS = 1;
