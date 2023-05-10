from api.models import FriendRequest


def create_friend_request(user_from, user_to):
    friend_request = FriendRequest.objects.create(
        user=user_from,
        to=user_to,
    )
    friend_request.save()


def get_friend_request(user_from, user_to):
    return FriendRequest.objects.filter(
        user=user_from,
        to=user_to
    ).first()


def decline_friend_request(friend_request):
    friend_request.is_accepted = True
    friend_request.is_declined = True
    friend_request.save()


def accept_friend(user, following_user):
    user.friends.add(following_user)
    user.save()
    create_friend_request(
        user_from=user,
        user_to=following_user)
    friend_request = FriendRequest.objects.filter(
        user=following_user,
        to=user
    ).first()
    friend_request.is_accepted = True
    friend_request.is_declined = False
    friend_request.save()


def delete_friend(user, friend):
    user.friends.remove(friend)
    user.save()
    get_friend_request(
        user_from=user,
        user_to=friend
    ).delete()
    decline_friend_request(get_friend_request(friend, user))


def accept_friend_request(user, following_user, incoming_friend_request):
    create_friend_request(user, following_user)
    user.friends.add(following_user)
    user.save()
    incoming_friend_request.is_accepted = True
    incoming_friend_request.is_declined = False
    incoming_friend_request.save()
