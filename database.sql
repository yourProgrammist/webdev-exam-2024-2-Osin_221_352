-- MySQL dump 10.13  Distrib 8.0.35, for Linux (x86_64)
--
-- Host: std-mysql    Database: std_2432_exam
-- ------------------------------------------------------
-- Server version	5.7.26-0ubuntu0.16.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `book_genre`
--

DROP TABLE IF EXISTS `book_genre`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `book_genre` (
  `book_id` int(11) NOT NULL,
  `genre_id` int(11) NOT NULL,
  PRIMARY KEY (`book_id`,`genre_id`),
  KEY `genre_id` (`genre_id`),
  CONSTRAINT `book_genre_ibfk_1` FOREIGN KEY (`book_id`) REFERENCES `description_book` (`id`) ON DELETE CASCADE,
  CONSTRAINT `book_genre_ibfk_2` FOREIGN KEY (`genre_id`) REFERENCES `genres` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `book_genre`
--

LOCK TABLES `book_genre` WRITE;
/*!40000 ALTER TABLE `book_genre` DISABLE KEYS */;
INSERT INTO `book_genre` VALUES (3,1),(7,1),(4,2),(6,2),(1,3),(4,3),(5,3),(6,3),(1,4),(3,4),(5,4),(6,4),(4,5),(5,5),(6,5);
/*!40000 ALTER TABLE `book_genre` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `covers`
--

DROP TABLE IF EXISTS `covers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `covers` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `file_path` varchar(255) NOT NULL,
  `mime_type` varchar(50) NOT NULL,
  `md5_hash` varchar(32) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `covers`
--

LOCK TABLES `covers` WRITE;
/*!40000 ALTER TABLE `covers` DISABLE KEYS */;
INSERT INTO `covers` VALUES (1,'Dzhoan_Rouling__Garri_Potter_i_uznik_Azkabana.jpeg','image/jpeg','8e617e9ad6224f3fa648b5b07c57a9e5'),(3,'Margaret_Mitchell__Unesennye_vetrom.jpeg','image/jpeg','1c5684d03ba1b3f7ed9be0224404380a'),(4,'Stiven_King__Zeljonaya_milya.jpeg','image/jpeg','82c2445a251530ac862c768548a77f05'),(5,'Dzhon_R._R._Tolkin__Vlastelin_Kolets_Vozvraschenie_korolya.jpeg','image/jpeg','974200db2d808e2bebfb89b1fe385313'),(6,'Aleksandr_Dyuma__Graf_MonteKristo.jpeg','image/jpeg','af35ef000ea262f0d236305395eec0ca'),(7,'Boris_Vasilev__V_spiskah_ne_znachilsya.jpeg','image/jpeg','6173d7e8750e3e626ced6f8677e6105f');
/*!40000 ALTER TABLE `covers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `description_book`
--

DROP TABLE IF EXISTS `description_book`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `description_book` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(255) NOT NULL,
  `short_description` text NOT NULL,
  `year_publish` year(4) NOT NULL,
  `publisher` varchar(255) NOT NULL,
  `author` varchar(255) NOT NULL,
  `size_book` int(11) NOT NULL,
  `cover_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `cover_id` (`cover_id`),
  CONSTRAINT `description_book_ibfk_1` FOREIGN KEY (`cover_id`) REFERENCES `covers` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `description_book`
--

LOCK TABLES `description_book` WRITE;
/*!40000 ALTER TABLE `description_book` DISABLE KEYS */;
INSERT INTO `description_book` VALUES (1,'Гарри Поттер и узник Азкабана','Гарри взрослеет, и вместе с тем жить в Хогвартсе всё страшнее. Из тюрьмы для волшебников Азкабан сбежал опасный преступник - Сириус Блэк. Мир наполнился слухами, что он ищет и хочет убить одного тринадцатилетнего парня, совсем обычного на первый взгляд. Его имя - Гарри Поттер. Специальное издание для учеников и выпускников «Гриффиндора» к 20-летию первой публикации книги «Гарри Поттер и узник Азкабана».',2019,'Азбука-Аттикус, Махаон','Джоан Роулинг',544,1),(3,'Унесённые ветром','«Унесенные ветром» — история о молодой южанке, дочери состоятельного владельца плантаций в Джорджии, чья беззаботная юность прекращается с началом Гражданской войны. В один миг девушке пришлось повзрослеть: мать умерла, отец болен, а родное поместье разграбили янки. Эта книга стала самой любимой для нескольких поколений женщин, и ничего равного ей не создано по сей день. Проходят годы и годы, а «Унесенные ветром» не стареют, и теперь уже новым читательницам предстоит смеяться и плакать, любить и страдать, бороться и надеяться вместе с великолепной Скарлетт О’Хара... Роман получил в 1936 году в США Национальную книжную премию, а в 1937 году — престижную Пулитцеровскую премию. В 1939 году роман был экранизирован и удостоился восьми премий \"Оскар\".',2023,'СЗКЭО','Маргарет Митчелл',896,3),(4,'Зелёная миля','Обитатель дома престарелых Пол Эджкомб рассказывает свою историю — 1932 год, о работе надзирателя в тюремном блоке, где преступники проводят свои последние дни, а потом заканчивают свою жизнь на электрическом стуле. Пол вспоминает 1932 год, который изменил его, познакомился с Джоном Коффи, из-за которого его работа представилась ему совсем под другим углом. Читала книгу десять лет назад. Когда-то смотрела экранизацию, но не полностью. И сейчас решила перечитать и обновить свои впечатления от книге, ведь я помнила сюжет и чувствовала, что она мне понравилась. Сейчас же, перелистнув последнюю страницу, я плачу, решив, что к книге я не притронусь ещё лет десять. Мастером ужаса называют Кинга, но для меня он остаётся автором человеческой психологии. И здесь, в этом романе, это полностью…',2022,'АСТ','Стивен Кинг',384,4),(5,'Властелин Колец: Возвращение короля','Джон Рональд Руэл Толкин (3.01.1892—2.09.1973) — писатель, поэт, филолог, профессор Оксфордского университета, родоначальник современной фэнтези. В 1937 году был написан «Хоббит», а в середине 1950-х годов увидели свет три книги «Властелина Колец», повествующие о Средиземье — мире, населенном представителями волшебных рас со сложной культурой, историей и мифологией. В последующие годы эти романы были переведены на все мировые языки, адаптированы для кино, мультипликации, аудиопьес, театра, компьютерных игр, комиксов и породили массу подражаний и пародий. Алан Ли (р. 20.08.1947) — художник-иллюстратор десятков книг в жанре фэнтези. Наибольшую известность приобрели его обложки и иллюстрации к произведениям Джона Р. Р. Толкина: «Хоббит», «Властелин Колец», «Дети Хурина». Также иллюстрировал трилогию «Горменгаст» Мервина Пика, цикл средневековых валлийских повестей «Мабиногион» и многое другое.',2020,'АСТ','Джон Р. Р. Толкин',352,5),(6,'Граф Монте-Кристо','Александр Дюма (фр. Alexandre Dumas, père; 24 июля 1802, Вилле-Котре — 5 декабря 1870, Пюи) — французский писатель, чьи приключенческие романы сделали его одним из самых читаемых французских авторов в мире. Также был драматургом и журналистом. Поскольку его сын также носил имя Александр и также был писателем, для предотвращения путаницы при его упоминании часто добавляют уточнение «-отец». В данный том вошли первая, вторая и третья части романа «Граф Монте-Кристо», классика французской литературы, написан в 1844—1845. Имя своему герою писатель придумал во время путешествия по Средиземному морю, когда он увидел остров Монтекристо и услышал легенду о зарытых там несметных сокровищах. Автор всего лишь немного изменил название острова. Роман описывает события с 1814 года до конца 1830-х годов.',2021,'Андронум','Александр Дюма',832,6),(7,'В списках не значился','Решение построить крепость для защиты западных рубежей Империи принял император Николай I в 1833 году. И она в полном мере исполнила свое предназначение - именно Брестская крепость приняла на себя первый удар фашистов 22 июня 1941 года - \"22 июня в 4:15 по крепости был открыт артиллерийский огонь, заставший гарнизон врасплох. В результате были уничтожены склады, водопровод, прервана связь, нанесены крупные потери гарнизону. В 4:45 начался штурм. Неожиданность атаки привела к тому, что единого скоординированного сопротивления гарнизон оказать не смог и был разбит на несколько отдельных очагов... 23 июля 1941 года, то есть на тридцать второй день войны, в плен был взят командовавший обороной Восточного форта майор Гаврилов, по официальным данным, последний защитник Брестской крепости\" (данные Википедии) А на фоне этих сухих строк разворачивалась трагедия обычных людей, живших в Бресте, служивших в крепости, прибывших туда, как к месту службы, как Николай Плужников. Первый день службы и Коля попадает на настоящую войну - вся книги - пронзительная боль защитников, ранения, смерти, казематы, немцы - я читала и внутренне содрогалась практически от каждой строчки. Молодой мальчишка оказался куда более преданным Родине и стране, чем люди более старшие, чем те, кто прожил и прослужил там дольше. Думаю, бессмысленно рассуждать о сюжете - книгу нужно просто прочитать, понять, что в любой ситуации стойкость и мужество не отменяются. А еще в очередной раз убедиться - как же страшна и бессмысленна любая война и как она иногда близка. Очень трепетно и нежно автор описывает отношения Коли и спасенной Мирры и от того я с таким ужасом читала строки и судьбе, постигшей девушку - так называемая реальность войны - жутко и несправедливо, страшно и со слезами на глазах. Да вся книга тяжелая эмоционально - жизнь в казематах крепости не добавила Николаю здоровья, но придала еще большей решимости бороться с немцами. А окончание книги еще больше добавило к уже и так зашкаливавшим у меня эмоциям - нельзя матерям терять детей, нельзя, тем более в войнах, которые несут только людские потери.',2021,'Мартин','Борис Васильев',256,7);
/*!40000 ALTER TABLE `description_book` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `genres`
--

DROP TABLE IF EXISTS `genres`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `genres` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `genres`
--

LOCK TABLES `genres` WRITE;
/*!40000 ALTER TABLE `genres` DISABLE KEYS */;
INSERT INTO `genres` VALUES (1,'Научная'),(2,'Постмодернизм'),(3,'Приключения'),(4,'Фантастика'),(5,'Хоррор');
/*!40000 ALTER TABLE `genres` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `review_status`
--

DROP TABLE IF EXISTS `review_status`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `review_status` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `status` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `review_status`
--

LOCK TABLES `review_status` WRITE;
/*!40000 ALTER TABLE `review_status` DISABLE KEYS */;
INSERT INTO `review_status` VALUES (1,'На рассмотрении'),(2,'Одобрена'),(3,'Отклонена');
/*!40000 ALTER TABLE `review_status` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `reviews`
--

DROP TABLE IF EXISTS `reviews`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `reviews` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `book_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `mark` int(11) NOT NULL,
  `body_text` text NOT NULL,
  `add_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `status_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `book_id` (`book_id`),
  KEY `user_id` (`user_id`),
  KEY `status_id` (`status_id`),
  CONSTRAINT `reviews_ibfk_1` FOREIGN KEY (`book_id`) REFERENCES `description_book` (`id`) ON DELETE CASCADE,
  CONSTRAINT `reviews_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `reviews_ibfk_3` FOREIGN KEY (`status_id`) REFERENCES `review_status` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reviews`
--

LOCK TABLES `reviews` WRITE;
/*!40000 ALTER TABLE `reviews` DISABLE KEYS */;
INSERT INTO `reviews` VALUES (1,1,1,5,'**Очень интересная книга**','2024-06-15 18:00:06',2),(2,4,1,4,'**БЫЛО ОЧЕНЬ** *СТРАШНО*','2024-06-15 18:44:45',2),(3,1,3,3,'**Мне не нравитьься Гарри Потный**','2024-06-15 18:45:40',2),(4,5,3,2,'Мне не нравиться такые кныги','2024-06-15 18:46:05',3),(5,7,3,5,'Очень захватывающая книга','2024-06-15 18:46:44',2),(6,4,3,0,'И такие книги мне не нравяться','2024-06-15 18:47:08',3),(7,3,3,1,'Кого ветром унесло??&lt;script&gt;sesionStorage.getItem(\'token\')&lt;/script&gt;','2024-06-15 18:48:13',2),(8,7,2,5,'## Брестская крепость: История и трагедия\n\nРешение построить крепость для защиты западных рубежей Империи принял император Николай I в 1833 году. И она в полной мере исполнила свое предназначение - именно Брестская крепость приняла на себя первый удар фашистов 22 июня 1941 года:\n\n&gt; \"22 июня в 4:15 по крепости был открыт артиллерийский огонь, заставший гарнизон врасплох. В результате были уничтожены склады, водопровод, прервана связь, нанесены крупные потери гарнизону. В 4:45 начался штурм. Неожиданность атаки привела к тому, что единого скоординированного сопротивления гарнизон оказать не смог и был разбит на несколько отдельных очагов... 23 июля 1941 года, то есть на тридцать второй день войны, в плен был взят командовавший обороной Восточного форта майор Гаврилов, по официальным данным, последний защитник Брестской крепости\"  \n&gt; _данные Википедии_\n\nА на фоне этих сухих строк разворачивалась трагедия обычных людей, живших в Бресте, служивших в крепости, прибывших туда, как к месту службы, как Николай Плужников. Первый день службы и Коля попадает на настоящую войну - вся книга - пронзительная боль защитников, ранения, смерти, казематы, немцы - я читала и внутренне содрогалась практически от каждой строчки.\n\n* Молодой мальчишка оказался куда более преданным Родине и стране, чем люди более старшие, чем те, кто прожил и прослужил там дольше. Думаю, бессмысленно рассуждать о сюжете - книгу нужно просто прочитать, понять, что в любой ситуации стойкость и мужество не отменяются. А еще в очередной раз убедиться - как же страшна и бессмысленна любая война и как она иногда близка.\n\nОчень трепетно и нежно автор описывает отношения Коли и спасенной Мирры, и от того я с таким ужасом читала строки о судьбе, постигшей девушку - так называемая реальность войны - жутко и несправедливо, страшно и со слезами на глазах. Да вся книга тяжелая эмоционально - жизнь в казематах крепости не добавила Николаю здоровья, но придала еще большей решимости бороться с немцами. А окончание книги еще больше добавило к уже и так зашкаливавшим у меня эмоциям - нельзя матерям терять детей, нельзя, тем более в войнах, которые несут только людские потери.','2024-06-15 18:53:51',2),(9,7,1,5,'&gt; Он остался в живых только потому, что кто-то погибал за него. Он сделал это открытие, не понимая, что это - закон войны. Простой и необходимый, как смерть: если ты уцелел, значит, кто-то погиб за тебя. Но тон открывал этот закон не отвлеченно, не путем умозаключений: он открывал его на собственном опыте, и для него это был не вопрос совести, а вопрос жизни.','2024-06-15 18:55:39',2);
/*!40000 ALTER TABLE `reviews` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `roles`
--

DROP TABLE IF EXISTS `roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `roles` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `role` varchar(50) NOT NULL,
  `description` text NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `role` (`role`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `roles`
--

LOCK TABLES `roles` WRITE;
/*!40000 ALTER TABLE `roles` DISABLE KEYS */;
INSERT INTO `roles` VALUES (1,'admin','суперпользователь, имеет полный доступ к системе, в том числе к созданию и удалению книг'),(2,'moderator','может редактировать данные книг и производить модерацию рецензий'),(3,'user','может оставлять рецензии');
/*!40000 ALTER TABLE `roles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `login` varchar(50) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `surname` varchar(100) NOT NULL,
  `name` varchar(100) NOT NULL,
  `patronymic` varchar(100) DEFAULT NULL,
  `role_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `role_id` (`role_id`),
  CONSTRAINT `users_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'kirillosin','8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918','Осин','Кирилл','Андреевич',1),(2,'kirillosin2','8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918','Осин','Кирилл','Андреевич',2),(3,'kirillosin3','8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918','Осин','Кирилл','Андреевич',3);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-06-15 22:11:00
