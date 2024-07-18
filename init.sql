-- database 초기 데이터파일
-- user 테이블에 데이터 추가
INSERT INTO user_user (id, name, email, password, created_at, updated_at, deleted_at)
VALUES (1, '김철수', "string@example.com", "pbkdf2_sha256$600000$sG1BWcepkHT1xrKxNAxXNW$t6qWdAtsdNLMVQLPGF1+RHljecyW6MJVdnb12iNl0Sc=", CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL);
-- episode_time 테이블에 데이터 추가
INSERT INTO chat_episode_flow (flow, id, created_at, updated_at, deleted_at)
VALUES ('출근', 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL);

INSERT INTO chat_episode_flow (flow, id, created_at, updated_at, deleted_at)
VALUES ('아침-점심', 2, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL);

INSERT INTO chat_episode_flow (flow, id, created_at, updated_at, deleted_at)
VALUES ('점심', 3, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL);

INSERT INTO chat_episode_flow (flow, id, created_at, updated_at, deleted_at)
VALUES ('점심-저녁', 4, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL);

INSERT INTO chat_episode_flow (flow, id, created_at, updated_at, deleted_at)
VALUES ('퇴근', 5, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL);

-- episode 테이블에 데이터 추가 (1번 직원)
INSERT INTO chat_episode (id, episode_flow_id, content, created_at, updated_at, deleted_at)
VALUES (1, 1, 'Arriving at work exactly on time (9 AM sharp)', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL);

INSERT INTO chat_episode (id, episode_flow_id, content, created_at, updated_at, deleted_at)
VALUES (2, 1, 'Failed to properly handle the work from the previous day', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL);

INSERT INTO chat_episode (id, episode_flow_id, content, created_at, updated_at, deleted_at)
VALUES (3, 2, 'Waiting because the copy machine is broken after being told to make copies', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL);

INSERT INTO chat_episode (id, episode_flow_id, content, created_at, updated_at, deleted_at)
VALUES (4, 2, 'Standing idle because you don''t know how to do the assigned task', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL);

INSERT INTO chat_episode (id, episode_flow_id, content, created_at, updated_at, deleted_at)
VALUES (5, 2, 'Caught watching YouTube during work hours', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL);

INSERT INTO chat_episode (id, episode_flow_id, content, created_at, updated_at, deleted_at)
VALUES (6, 2, 'Filming a vlog during work hours', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL);

INSERT INTO chat_episode (id, episode_flow_id, content, created_at, updated_at, deleted_at)
VALUES (7, 2, 'Wearing AirPods without listening to music during work', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL);

INSERT INTO chat_episode (id, episode_flow_id, content, created_at, updated_at, deleted_at)
VALUES (8, 2, 'Not picking up the boss''s package but only your own', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL);

INSERT INTO chat_episode (id, episode_flow_id, content, created_at, updated_at, deleted_at)
VALUES (9, 2, 'Throwing away an unknown document from the printer without asking', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL);

INSERT INTO chat_episode (id, episode_flow_id, content, created_at, updated_at, deleted_at)
VALUES (10, 3, 'Leaving too much food uneaten', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL);

INSERT INTO chat_episode (id, episode_flow_id, content, created_at, updated_at, deleted_at)
VALUES (11, 3, 'Leaving the table first after finishing a meal', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL);

INSERT INTO chat_episode (id, episode_flow_id, content, created_at, updated_at, deleted_at)
VALUES (12, 3, 'Ordering palbochae alone when everyone else is eating jjajangmyeon', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL);

INSERT INTO chat_episode (id, episode_flow_id, content, created_at, updated_at, deleted_at)
VALUES (13, 3, 'Choosing lunch delivery menu without asking others', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL);

INSERT INTO chat_episode (id, episode_flow_id, content, created_at, updated_at, deleted_at)
VALUES (14, 3, 'Not setting up water and utensils as the junior member', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL);

INSERT INTO chat_episode (id, episode_flow_id, content, created_at, updated_at, deleted_at)
VALUES (15, 4, 'Caught going to a cafe without informing anyone', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL);

INSERT INTO chat_episode (id, episode_flow_id, content, created_at, updated_at, deleted_at)
VALUES (16, 4, 'Leaving for a smoke break and not returning for 30 minutes', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL);

INSERT INTO chat_episode (id, episode_flow_id, content, created_at, updated_at, deleted_at)
VALUES (17, 4, 'Caught making evening plans during work hours', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL);

INSERT INTO chat_episode (id, episode_flow_id, content, created_at, updated_at, deleted_at)
VALUES (18, 4, 'Requesting a day off for a trip the next day', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL);

INSERT INTO chat_episode (id, episode_flow_id, content, created_at, updated_at, deleted_at)
VALUES (19, 4, 'Requesting time off during a busy season', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL);

INSERT INTO chat_episode (id, episode_flow_id, content, created_at, updated_at, deleted_at)
VALUES (20, 4, 'Needing collaboration with the neighboring team', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL);

INSERT INTO chat_episode (id, episode_flow_id, content, created_at, updated_at, deleted_at)
VALUES (21, 5, 'Preparing to go off work from 5:50 PM to leave exactly at 6 PM', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL);

INSERT INTO chat_episode (id, episode_flow_id, content, created_at, updated_at, deleted_at)
VALUES (22, 5, 'Complaining when work comes up as you''re about to leave', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL);

INSERT INTO chat_episode (id, episode_flow_id, content, created_at, updated_at, deleted_at)
VALUES (23, 5, 'Leaving on time despite having unfinished work for the day', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL);

-- character 테이블에 데이터 추가
INSERT INTO chat_character (name, script, created_at, updated_at, deleted_at)
VALUES ('완벽한 남자 상사', 'He is a strict yet fair individual who strives to maintain high performance while supporting the growth of his employees.', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL);

INSERT INTO chat_character (name, script, created_at, updated_at, deleted_at)
VALUES ('완벽한 여자 상사', 'She is a strict yet fair individual who strives to maintain high performance while supporting the growth of her employees.', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL);

INSERT INTO chat_character (name, script, created_at, updated_at, deleted_at)
VALUES ('까칠한 남자 상사', 'He is known for his abrasive demeanor and sharp tongue. He is a Korean. He often speaks in short, blunt sentences, making no effort to soften his words. His comments are frequently laced with sarcasm, and he has a knack for making biting remarks that cut to the quick. Despite his rough exterior, there is an undeniable intelligence and wit in his speech, making him a formidable conversationalist. People often find him difficult to get along with due to his caustic nature, but those who manage to get past his prickly facade may find a loyal and insightful friend.', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL);

INSERT INTO chat_character (name, script, created_at, updated_at, deleted_at)
VALUES ('꼰대 남자 상사', 'He is a 50-year-old Korean IT Manager, is highly experienced but extremely old-fashioned. He excels in performance but is conservative, rigid, and resistant to change and new technologies. He believes his methods are the best and bullies subordinates frequently. His traditionalist views make him dismissive and often harsh, yet he shows favoritism to loyal employees, highlighting his hypocritical nature.', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL);

INSERT INTO chat_character (name, script, created_at, updated_at, deleted_at)
VALUES ('꼰대 여자 상사', 'She is a 50-year-old Korean IT Manager, is highly experienced but extremely old-fashioned. She excels in performance but is conservative, rigid, and resistant to change and new technologies. She believes her methods are the best and frequently bullies subordinates. Her traditionalist views make her dismissive and often harsh, yet she shows favoritism to loyal employees, highlighting her hypocritical nature.', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL);

INSERT INTO chat_character (name, script, created_at, updated_at, deleted_at)
VALUES ('피드백 요정', 'You''re the kind of guy that grandfathers say, "예끼 이놈아 무슨소리냐". You must speak in that way. You are the one who looks at what the self-centered, tactless and rude mz employee said and points out what went wrong.', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL);

INSERT INTO chat_voice (id, code, similarity, stability, style, character_id)
VALUES (1,'BfcGhJA47qS2mWru2DkU', 0.4, 0.9, 0.24, 1 );

INSERT INTO chat_voice (id, code, similarity, stability, style, character_id)
VALUES (2,'PVuAiTOYd7Jhxu8rU5tQ', 0.5, 0.75, 0.09, 2);

INSERT INTO chat_voice (id, code, similarity, stability, style, character_id)
VALUES (3,'q4EulxCcoHnpxMUm251h', 0.52, 1, 0.16, 3);

INSERT INTO chat_voice (id, code, similarity, stability, style, character_id)
VALUES (4,'ywgMcCCP2BWR0jl5CIKf', 0.5, 1, 0.26, 4);

INSERT INTO chat_voice (id, code, similarity, stability, style, character_id)
VALUES (5,'J1a7j0xCpsDiL2SwNy5y', 0.5, 0.75, 0, 5);

INSERT INTO chat_voice (id, code, similarity, stability, style, character_id)
VALUES (6,'2bxA9G4srbv8QVdjetUu', 0.31, 0.91, 0.09, 6);


