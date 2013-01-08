CREATE TABLE Users (
	Username CHAR(20) NOT NULL,
	Email CHAR(50) NOT NULL,
	PasswordHash VARCHAR(200) NOT NULL,

	PRIMARY KEY (Username)
);

CREATE TABLE Problems (
	Name CHAR(15) NOT NULL,
	ProblemStatement TEXT NOT NULL,
	Description TEXT NOT NULL,
	PRIMARY KEY (Name)
);

CREATE TABLE Submissions (
	Username CHAR(20) NOT NULL,
	ProblemName Char(15) NOT NULL
);

ALTER TABLE Submissions
ADD FOREIGN KEY (ProblemName) REFERENCES Problems(Name);

ALTER TABLE Submissions
ADD FOREIGN KEY (Username) REFERENCES Users(Username);