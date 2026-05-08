from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.urls import reverse
from Connectly.models import Profile, Post, Comment
from Connectly.forms import PostForm, SignUpForm, ProfileEditForm, UserEditForm, CommentForm
from django.contrib.auth import authenticate, login, logout
from google.cloud import recaptchaenterprise_v1
from google.cloud.recaptchaenterprise_v1 import Assessment
from google.oauth2 import service_account
from allauth.socialaccount.models import SocialAccount
from allauth.account.utils import user_email
from .utils import generate_otp_code, send_otp_email
from django.contrib.auth.models import User
from django.core.mail import send_mail
from google.cloud import recaptchaenterprise_v1
from django.db.models import Q

def create_assessment(
        project_id: str, recaptcha_key: str, token: str, recaptcha_action: str
):    #google recaptcha
    client = recaptchaenterprise_v1.RecaptchaEnterpriseServiceClient()

    event = recaptchaenterprise_v1.Event()
    event.site_key = recaptcha_key  # Replace with your reCAPTCHA Site Key
    event.token = token  # Token received from the frontend

    # Create an assessment object and link it to the event
    assessment = recaptchaenterprise_v1.Assessment()
    assessment.event = event

    # Define the project name in the correct format
    project_name = f"projects/{project_id}"  # Replace with your Google Cloud Project ID

    # Build the assessment request
    request = recaptchaenterprise_v1.CreateAssessmentRequest()
    request.assessment = assessment
    request.parent = project_name

    # Call Google reCAPTCHA Enterprise to create the assessment
    response = client.create_assessment(request)

    # Check if the token is valid
    if not response.token_properties.valid:
        print(
            "The CreateAssessment call failed because the token was "
            + "invalid for the following reasons: "
            + str(response.token_properties.invalid_reason)
        )
        return None

    # Check if the expected action was executed
    if response.token_properties.action != recaptcha_action:
        print(
            "The action attribute in your reCAPTCHA tag does"
            + "not match the action you are expecting to score"
        )
        return None
    else:
        # Get the risk score and the reasons for the score
        for reason in response.risk_analysis.reasons:
            print(reason)
        print("The reCAPTCHA score for this token is: " + str(response.risk_analysis.score))

        # Get the assessment name (optional, for debugging or future use)
        assessment_name = client.parse_assessment_path(response.name).get("assessment")
        print(f"Assessment name: {assessment_name}")
    return response

def validate_recaptcha(token, recaptcha_action):        #google recaptcha
    project_id = "my-project-81083-1738152303405"
    recaptcha_key = "6Ldoi8YqAAAAAHGvvhEBehqL1NbPrqwwL18zOZF7"
    assessment = create_assessment(project_id, recaptcha_key, token, recaptcha_action)

    if assessment is None:
        return False

    # Check the risk score (e.g., allow only if the score is >= 0.5)
    score = assessment.risk_analysis.score
    print(f"reCAPTCHA risk score for action '{recaptcha_action}': {score}")
    return score >= 0.5


def welcome(request):           #page for non logged in users
    context = {
        'title': 'Connectly',
    }
    if request.user.is_authenticated:
        instance = get_object_or_404(Profile, user=request.user)
        return redirect(f'profile/{instance.user_id}')
    else:
        if request.method == 'POST':
            recaptcha_token = request.POST.get('recaptcha_token')

            if not validate_recaptcha(recaptcha_token, "CONTACT"):
                messages.error(request, 'reCAPTCHA validation failed. Please try again.')
                return redirect('welcome')
            else:
                email = request.POST.get('email')
                name = request.POST.get('name')
                subject = request.POST.get('subject')
                message = request.POST.get('message')
                send_mail(f'{name}, ' + subject, message, email, ['markosysak@gmail.com'])
                messages.success(request, f"Thanks for contacting us {name} we'll reply shortly")
        return render(request,'welcome_page.html', context)

def profile(request, user_id):        #profile page
    if request.user.is_authenticated:
        profile = Profile.objects.get(user_id=user_id)
        follows=len(profile.follows.all())
        followed_by=len(profile.followed_by.all())
        posts=Post.objects.filter(author=user_id).order_by('-created')
        num_posts=Post.objects.filter(author=user_id).count()
        media_posts=Post.objects.filter(author_id=user_id, media_file__iregex=r'\.(jpg|jpeg|png|gif|mp4|mov|avi|mkv)$').order_by('-created')
        audio_posts=Post.objects.filter(author_id=user_id,media_file__iregex=r'\.(mp3|wav|ogg)$').order_by('-created')
        audio_combined=zip(audio_posts,posts)
        liked_posts=Post.objects.filter(likes__id=profile.user_id)
        user=User.objects.get(id=user_id)
        context = {
            'num_posts': num_posts,
            'profile': profile,
            'follows': follows,
            'followed_by': followed_by,
            'posts': posts,
            'media_posts': media_posts,
            'audio_posts': audio_posts,
            'audio_combined': audio_combined,
            'liked_posts': liked_posts,
            'user': user,
        }
        if request.user.profile.user_id == profile.user_id:
            if request.path.endswith(f'/{request.user.id}/'):
                return render(request, 'your_profile.html', context)
            elif request.path.endswith(f'/{request.user.id}/audios/'):
                return render(request, 'your_profile_audios.html', context)
            elif request.path.endswith(f'/{request.user.id}/likes/'):
                return render(request, 'your_profile_likes.html', context)
        else:
            if request.method == 'POST':
                current_user = request.user.profile
                action = request.POST['follow']
                if action == 'unfollow':
                    current_user.follows.remove(profile)
                elif action == 'follow':
                    current_user.follows.add(profile)
                current_user.save()
                return redirect('profile', profile.user_id)
            if request.path.endswith(f'/{profile.user_id}/'):
                return render(request, 'profile.html', context)
            elif request.path.endswith(f'/{profile.user_id}/audios/'):
                return render(request, 'profile_audios.html', context)
            elif request.path.endswith(f'/{profile.user_id}/likes/'):
                return render(request, 'profile_likes.html', context)
    else:
        messages.success(request, 'You are not logged in')
        return redirect('welcome')
  #follows page
def follows(request, user_id):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user_id=user_id)
        return render(request, 'follows.html', {'profile': profile})
    else:
        messages.success(request, 'You are not logged in')
        return redirect('welcome')
def followed(request, user_id):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user_id=user_id)
        return render(request, 'following.html', {'profile': profile})
    else:
        messages.success(request, 'You are not logged in')
        return redirect('welcome')
def home(request):              #main page where the posts r displayed
    if request.user.is_authenticated:
        posts=Post.objects.all().order_by('-created')
        if request.method == 'POST':
            current_user = request.user
            target_user_id = request.POST.get('target_user_id')
            action = request.POST.get('follow')
            action_post = request.POST.get('like')
            target_profile = Profile.objects.get(user_id=target_user_id)
            target_post_id = request.POST.get('target_post_id')
            if target_post_id:
                target_post = Post.objects.get(id=target_post_id)
                if action_post == 'like':
                    target_post.likes.add(current_user.profile)
                elif action_post == 'unlike':
                    target_post.likes.remove(current_user.profile)

            if action == 'unfollow':
                current_user.profile.follows.remove(target_profile)
            elif action == 'follow':
                current_user.profile.follows.add(target_profile)
            current_user.save()

        return render(request,'home.html',{'posts':posts})
    else:
        messages.success(request, 'You are not logged in')
        return redirect('welcome')
def post_create(request):           #post creation form
    if request.user.is_authenticated:
        form = PostForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Your post has been created!')
            return redirect('home')
        return render(request, 'post_create.html', {'form': form})
    else:
        messages.success(request, 'You are not logged in')
        return redirect('welcome')
def login_user(request):
    if request.user.is_authenticated:
        return redirect(reverse('profile', kwargs={'user_id': request.user.profile.user_id}))

    if request.method == 'POST':
        username_or_email = request.POST['username']
        password = request.POST['password']
        recaptcha_token = request.POST.get('recaptcha_token')

        if not validate_recaptcha(recaptcha_token, "LOGIN"):
            messages.error(request, 'reCAPTCHA validation failed. Please try again.')
            return redirect('login')

        user = None

        if "@" in username_or_email:
            try:
                user_obj = User.objects.get(email=username_or_email)
                user = authenticate(
                    request,
                    username=user_obj.username,
                    password=password
                )
            except User.DoesNotExist:
                user = None
        else:
            user = authenticate(
                request,
                username=username_or_email,
                password=password
            )

        if user is not None:
            login(
                request,
                user,
                backend='django.contrib.auth.backends.ModelBackend'
            )

            messages.success(request, 'You have been logged in successfully!')
            return redirect(reverse('profile', kwargs={'user_id': user.id}))
        else:
            messages.error(request, 'Invalid credentials. Please try again.')
            return redirect('login')

    return render(request, 'login.html')


def logout_user(request):    #logut func
    logout(request)
    messages.success(request, 'You have been logged out')
    return redirect('welcome')

def register_user(request):
    if request.user.is_authenticated:
        return redirect(reverse('profile', kwargs={'user_id': request.user.id}))

    initial = {}
    sociallogin = request.session.get('socialaccount_sociallogin')

    if sociallogin:
        extra_data = sociallogin['account']['extra_data']
        initial = {
            'first_name': extra_data.get('given_name', ''),
            'last_name': extra_data.get('family_name', ''),
            'email': extra_data.get('email', ''),
        }

    form = SignUpForm(request.POST or None, initial=initial)

    if request.method == 'POST':
        if form.is_valid():
            user = form.save(commit=False)
            user.first_name = form.cleaned_data.get('first_name')
            user.last_name = form.cleaned_data.get('last_name')

            # Temporary demo mode: account is activated immediately
            user.is_active = True
            user.save()

            login(request, user)

            messages.success(request, 'Account created successfully!')
            return redirect(reverse('profile', kwargs={'user_id': user.id}))
        else:
            messages.error(request, form.errors.as_text())

    return render(request, 'register.html', {'form': form})


def verify_otp(request):      #OTP verification
    if request.method == 'POST':
        user_entered_code = request.POST.get('otp_code')
        session_code = request.session.get('otp_code')
        tmp_user_id = request.session.get('tmp_user_id')

        if user_entered_code == session_code and tmp_user_id:
            try:
                user = User.objects.get(id=tmp_user_id)
                user.is_active = True
                user.save()
                if user.email and user.socialaccount_set.exists():
                    backend = 'allauth.account.auth_backends.AuthenticationBackend'
                else:
                    backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, user, backend=backend)
                del request.session['otp_code']
                del request.session['tmp_user_id']

                messages.success(request, 'you were successfully authenticated')
                return redirect(reverse('profile', kwargs={'user_id': user.id}))

            except User.DoesNotExist:
                messages.error(request, 'User does not exist. Please try again.')
                return redirect('register')

        else:
            messages.error(request, 'Invalid OTP code. Please try again.')
            return redirect('verify_otp')

    return render(request, 'verify_otp.html')

def update_profile(request):
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        current_profile= Profile.objects.get(user_id=current_user)

        user_form = UserEditForm(request.POST or None, request.FILES or None, instance=current_user)
        add_form = ProfileEditForm(request.POST or None, request.FILES or None, instance=current_profile)
        if user_form.is_valid() and add_form.is_valid():
            user_form.save()
            add_form.save()
            messages.success(request, 'Your profile has been updated')
            return redirect('home')
        else:
            user_form = UserEditForm(request.POST or None, request.FILES or None,instance=current_user)
            add_form = ProfileEditForm(request.POST or None, request.FILES or None,instance=current_profile)

        return render(request, 'profile_update.html', {'user_form': user_form, 'add_form': add_form})
    else:
        messages.success(request,'You are not logged in')
        return redirect('welcome')
def post_detail(request, id):
    if request.user.is_authenticated:
        instance = get_object_or_404(Post, id=id)
        comments= Comment.objects.filter(post=instance)
        form= CommentForm(request.POST or None)
        if request.method == 'POST':
            action = request.POST.get('follow')
            action_post = request.POST.get('like')
            action_delete = request.POST.get('delete')

            if form.is_valid():
                comment = form.save(commit=False)
                comment.author = request.user.profile
                comment.post=instance
                comment.save()
                form.clean()
                return redirect('post_detail', id)
            if action:
                if action == 'unfollow':
                    request.user.profile.follows.remove(instance.author.profile)
                elif action == 'follow':
                    request.user.profile.follows.add(instance.author.profile)
            if action_post:
                if action_post == 'like':
                    instance.likes.add(request.user.profile)
                elif action_post == 'unlike':
                    instance.likes.remove(request.user.profile)
            if action_delete:
                instance.delete()
                messages.success(request, 'Your post has been deleted')
                return redirect('home')
            request.user.save()
        return render(request, 'post_detail.html',{'instance':instance,'comments':comments,'form':form})
    else:
        messages.error(request, 'You are not logged in')
        return redirect('home')

def search(request):
    if request.user.is_authenticated:
        query = request.GET.get('q')
        if query:
            searched = User.objects.filter(Q(username__icontains=query))
            return render(request, 'search.html',{'searched':searched})
        else:
            return render(request, 'search.html')
    else:
        messages.success(request, 'You are not logged in')
        return redirect('welcome')