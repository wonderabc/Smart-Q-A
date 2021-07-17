import json
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from smart_Q_A_question_solve.preprocess_question import question
# Create your views here.


def main(request):
    return render(request, 'index.html')


@csrf_exempt  # post授权
def getreply(request):
    data = request.POST
    print(data)
    q = str(data.get("inputinfo"))  # 获得问题
    print(q)
    tmp = question()
    tmp.question_process(q)
    ans = tmp.answer
    print(ans)
    response = JsonResponse({"replyinfo": ans})
    return response
