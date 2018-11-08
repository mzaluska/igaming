from django.shortcuts import redirect


def welcome(request):
    if request.user.is_authenticated:
        return redirect('player_home')
    else:
        return redirect('player_login')
