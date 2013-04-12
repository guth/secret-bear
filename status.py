SUCCESS = 0
ANSWER_CORRECT = 10
WRONG_ANSWER = 11
COMPILE_ERROR = 12
RUNTIME_ERROR = 13
TIME_LIMIT_EXCEEDED = 14
INTERNAL_ERROR = 15

resultDict = {}
resultDict[ANSWER_CORRECT] = ("AC", "Answer Correct")
resultDict[WRONG_ANSWER] = ("WA", "Wrong Answer")
resultDict[COMPILE_ERROR] = ("CE", "Compilation Error")
resultDict[RUNTIME_ERROR] = ("RE", "Runtime Error")
resultDict[TIME_LIMIT_EXCEEDED] = ("TLE", "Time Limit Exceeded")
resultDict[INTERNAL_ERROR] = ("IE", "Internal Error")

def resultCodeToText(code):
	return resultDict.get(code)
