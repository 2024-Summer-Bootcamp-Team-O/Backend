-- database 초기 데이터파일

-- episode_time 테이블에 데이터 추가
INSERT INTO chat_episode_time (episode_flow, episode_time_id, created_at, updated_at, deleted_at)
VALUES ('출근', 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL);

INSERT INTO chat_episode_time (episode_flow, episode_time_id, created_at, updated_at, deleted_at)
VALUES ('아침-점심', 2, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL);

INSERT INTO chat_episode_time (episode_flow, episode_time_id, created_at, updated_at, deleted_at)
VALUES ('점심', 3, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL);

INSERT INTO chat_episode_time (episode_flow, episode_time_id, created_at, updated_at, deleted_at)
VALUES ('점심-저녁', 4, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL);

INSERT INTO chat_episode_time (episode_flow, episode_time_id, created_at, updated_at, deleted_at)
VALUES ('퇴근', 5, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL);

-- episode 테이블에 데이터 추가 (1번 직원)
INSERT INTO chat_episode (episode_time_id, episode_content, created_at, updated_at, deleted_at)
VALUES (1, 'Arriving at work exactly on time (9 AM sharp)', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL);

INSERT INTO chat_episode (episode_time_id, episode_content, created_at, updated_at, deleted_at)
VALUES (1, 'Failed to properly handle the work from the previous day', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL);

INSERT INTO chat_episode (episode_time_id, episode_content, created_at, updated_at, deleted_at)
VALUES (2, 'Waiting because the copy machine is broken after being told to make copies', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL);

INSERT INTO chat_episode (episode_time_id, episode_content, created_at, updated_at, deleted_at)
VALUES (2, 'Standing idle because you don''t know how to do the assigned task', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL);

INSERT INTO chat_episode (episode_time_id, episode_content, created_at, updated_at, deleted_at)
VALUES (2, 'Caught watching YouTube during work hours', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL);

INSERT INTO chat_episode (episode_time_id, episode_content, created_at, updated_at, deleted_at)
VALUES (2, 'Filming a vlog during work hours', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL);

INSERT INTO chat_episode (episode_time_id, episode_content, created_at, updated_at, deleted_at)
VALUES (2, 'Wearing AirPods without listening to music during work', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL);

INSERT INTO chat_episode (episode_time_id, episode_content, created_at, updated_at, deleted_at)
VALUES (2, 'Not picking up the boss''s package but only your own', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL);

INSERT INTO chat_episode (episode_time_id, episode_content, created_at, updated_at, deleted_at)
VALUES (2, 'Throwing away an unknown document from the printer without asking', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL);

INSERT INTO chat_episode (episode_time_id, episode_content, created_at, updated_at, deleted_at)
VALUES (3, 'Leaving too much food uneaten', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL);

INSERT INTO chat_episode (episode_time_id, episode_content, created_at, updated_at, deleted_at)
VALUES (3, 'Leaving the table first after finishing a meal', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL);

INSERT INTO chat_episode (episode_time_id, episode_content, created_at, updated_at, deleted_at)
VALUES (3, 'Ordering palbochae alone when everyone else is eating jjajangmyeon', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL);

INSERT INTO chat_episode (episode_time_id, episode_content, created_at, updated_at, deleted_at)
VALUES (3, 'Choosing lunch delivery menu without asking others', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL);

INSERT INTO chat_episode (episode_time_id, episode_content, created_at, updated_at, deleted_at)
VALUES (3, 'Not setting up water and utensils as the junior member', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL);

INSERT INTO chat_episode (episode_time_id, episode_content, created_at, updated_at, deleted_at)
VALUES (4, 'Caught going to a cafe without informing anyone', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL);

INSERT INTO chat_episode (episode_time_id, episode_content, created_at, updated_at, deleted_at)
VALUES (4, 'Leaving for a smoke break and not returning for 30 minutes', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL);

INSERT INTO chat_episode (episode_time_id, episode_content, created_at, updated_at, deleted_at)
VALUES (4, 'Caught making evening plans during work hours', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL);

INSERT INTO chat_episode (episode_time_id, episode_content, created_at, updated_at, deleted_at)
VALUES (4, 'Requesting a day off for a trip the next day', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL);

INSERT INTO chat_episode (episode_time_id, episode_content, created_at, updated_at, deleted_at)
VALUES (4, 'Requesting time off during a busy season', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL);

INSERT INTO chat_episode (episode_time_id, episode_content, created_at, updated_at, deleted_at)
VALUES (4, 'Needing collaboration with the neighboring team', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL);

INSERT INTO chat_episode (episode_time_id, episode_content, created_at, updated_at, deleted_at)
VALUES (5, 'Preparing to go off work from 5:50 PM to leave exactly at 6 PM', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL);

INSERT INTO chat_episode (episode_time_id, episode_content, created_at, updated_at, deleted_at)
VALUES (5, 'Complaining when work comes up as you''re about to leave', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL);

INSERT INTO chat_episode (episode_time_id, episode_content, created_at, updated_at, deleted_at)
VALUES (5, 'Leaving on time despite having unfinished work for the day', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL);

-- character 테이블에 데이터 추가
INSERT INTO chat_character (character_name, character_script, created_at, updated_at, deleted_at)
VALUES ('완벽한 남자 상사', 'He is a strict yet fair individual who strives to maintain high performance while supporting the growth of his employees.', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL);

INSERT INTO chat_character (character_name, character_script, created_at, updated_at, deleted_at)
VALUES ('완벽한 여자 상사', 'She is a strict yet fair individual who strives to maintain high performance while supporting the growth of her employees.', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL);

INSERT INTO chat_character (character_name, character_script, created_at, updated_at, deleted_at)
VALUES ('까칠한 남자 상사', 'He is known for his abrasive demeanor and sharp tongue. He is a Korean. He often speaks in short, blunt sentences, making no effort to soften his words. His comments are frequently laced with sarcasm, and he has a knack for making biting remarks that cut to the quick. Despite his rough exterior, there is an undeniable intelligence and wit in his speech, making him a formidable conversationalist. People often find him difficult to get along with due to his caustic nature, but those who manage to get past his prickly facade may find a loyal and insightful friend.', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL);

INSERT INTO chat_character (character_name, character_script, created_at, updated_at, deleted_at)
VALUES ('꼰대 남자 상사', 'Kim Jin-su, a 50-year-old Korean IT Manager, is highly experienced but extremely old-fashioned. He excels in performance but is conservative, rigid, and resistant to change and new technologies. He believes his methods are the best and bullies subordinates frequently. His traditionalist views make him dismissive and often harsh, yet he shows favoritism to loyal employees, highlighting his hypocritical nature.', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL);

INSERT INTO chat_character (character_name, character_script, created_at, updated_at, deleted_at)
VALUES ('꼰대 여자 상사', 'Kim Jin-sook, a 50-year-old Korean IT Manager, is highly experienced but extremely old-fashioned. She excels in performance but is conservative, rigid, and resistant to change and new technologies. She believes her methods are the best and frequently bullies subordinates. Her traditionalist views make her dismissive and often harsh, yet she shows favoritism to loyal employees, highlighting her hypocritical nature.', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL);
