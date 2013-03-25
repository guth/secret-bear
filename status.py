SUCCESS = 0
ANSWER_CORRECT = 10
WRONG_ANSWER = 11
COMPILE_ERROR = 12
RUNTIME_ERROR = 13
TIME_LIMIT_EXCEEDED = 14
INTERNAL_ERROR = 15

resultDict = {}
resultDict[ANSWER_CORRECT] = "Answer Correct"
resultDict[WRONG_ANSWER] = "Wrong Answer"
resultDict[COMPILE_ERROR] = "Compile Error"
resultDict[RUNTIME_ERROR] = "Runtime Error"
resultDict[TIME_LIMIT_EXCEEDED] = "Time Limit Exceeded"
resultDict[INTERNAL_ERROR] = "Internal Error"

def resultCodeToText(code):
	return resultDict.get(code)
