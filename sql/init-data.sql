INSERT INTO Users (Username, Email, PasswordHash) VALUES
('guth1', 'guthriea90@gmail.com', 'fooHash1'),
('guth2', 'guthriea91@gmail.com', 'fooHash2'),
('guth3', 'guthriea92@gmail.com', 'fooHash3');

INSERT INTO Problems (Name, ProblemStatement, Description) VALUES
('TEST', 'Print all the integers until a negative one is reached.', 'Print positive integers.'),
('SAMER08F', 'Samer problem statement.', 'Samer description.'),
('ROLLBACK', 'Rollback problem statement', 'Rollback description.'),
('NIMGAME', 'Play a game of nim!', 'Play the game of nim.');

INSERT INTO Submissions (Username, ProblemName) VALUES
('guth1', 'SAMER08F'),
('guth1', 'ROLLBACK'),
('guth2', 'NIMGAME'),
('guth3', 'SAMER08F'),
('guth3', 'NIMGAME');