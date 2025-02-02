from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from Connectly.models import Profile, Post
from Connectly.post_form import PostForm
from django.contrib.auth import authenticate, login, logout
from google.cloud import recaptchaenterprise_v1
from google.cloud.recaptchaenterprise_v1 import Assessment
from google.oauth2 import service_account

from google.cloud import recaptchaenterprise_v1

def create_assessment(
        project_id: str, recaptcha_key: str, token: str, recaptcha_action: str
):
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

def validate_recaptcha(token, recaptcha_action):
    # Replace these with your actual Google Cloud configuration
    project_id = "my-project-81083-1738152303405"  # Your actual Google Cloud Project ID
    recaptcha_key = "6Ldoi8YqAAAAAHGvvhEBehqL1NbPrqwwL18zOZF7"  # Your actual reCAPTCHA Site Key

    # Call create_assessment to validate the token
    assessment = create_assessment(project_id, recaptcha_key, token, recaptcha_action)

    if assessment is None:
        return False

    # Check the risk score (e.g., allow only if the score is >= 0.5)
    score = assessment.risk_analysis.score
    print(f"reCAPTCHA risk score for action '{recaptcha_action}': {score}")
    return score >= 0.5  # Adjust the threshold as needed


def welcome(request):
    context = {
        'title': 'Connectly',
    }
    if request.user.is_authenticated:
        instance = get_object_or_404(Profile, user=request.user)
        return redirect(f'profile/{instance.user_id}')
    else:
        return render(request,'welcome_page.html', context)

def profile(request, id):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user_id=id)
        follows=len(profile.follows.all())
        followed_by=len(profile.followed_by.all())
        posts=Post.objects.filter(author=id).order_by('-created')
        num_posts=Post.objects.filter(author=id).count()
        media_posts=Post.objects.filter(author_id=id, media_file__iregex=r'\.(jpg|jpeg|png|gif|mp4|mov|avi|mkv)$').order_by('-created')
        audio_posts=Post.objects.filter(author_id=id,media_file__iregex=r'\.(mp3|wav|ogg)$').order_by('-created')
        audio_combined=zip(audio_posts,posts)
        if request.user.profile.user_id == profile.user_id:
            if request.path.endswith(f'/{request.user.id}/'):
                return render(request, 'your_profile.html', {'profile': profile, 'follows':follows, 'followed_by':followed_by, 'num_posts':num_posts, 'media_posts':media_posts, 'audio_posts':audio_posts, 'audio_combined':audio_combined})
            elif request.path.endswith(f'/{request.user.id}/audios/'):
                return render(request, 'your_profile_audios.html', {'profile': profile, 'num_posts':num_posts, 'audio_posts':audio_posts, 'follows':follows, 'followed_by':followed_by, 'audio_combined':audio_combined})
        else:
            if request.method == 'POST':
                current_user = request.user.profile
                action = request.POST['follow']
                if action == 'unfollow':
                    current_user.follows.remove(profile)
                elif action == 'follow':
                    current_user.follows.add(profile)
                current_user.save()
            if request.path.endswith(f'/{profile.user_id}/'):
                return render(request, 'profile.html', {'profile': profile, 'follows':follows, 'followed_by':followed_by, 'media_posts': media_posts, 'num_posts':num_posts, 'audio_combined':audio_combined})
            elif request.path.endswith(f'/{profile.user_id}/audios/'):
                return render(request, 'profile_audios.html', {'profile': profile, 'follows':follows, 'followed_by':followed_by, 'audio_posts':audio_posts, 'num_posts':num_posts, 'audio_combined':audio_combined})
    else:
        messages.success(request, 'You are not logged in')
        return redirect('welcome')
def follows(request, id):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user_id=id)
        return render(request, 'follows.html', {'profile': profile})
    else:
        messages.success(request, 'You are not logged in')
        return redirect('welcome')
def followed(request, id):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user_id=id)
        return render(request, 'following.html', {'profile': profile})
    else:
        messages.success(request, 'You are not logged in')
        return redirect('welcome')
def home(request):
    if request.user.is_authenticated:
        posts=Post.objects.all().order_by('-created')
        if request.method == 'POST':
            current_user = request.user.profile
            target_user_id = request.POST.get('target_user_id')
            action = request.POST['follow']
            target_profile = Profile.objects.get(user_id=target_user_id)
            if action == 'unfollow':
                current_user.follows.remove(target_profile)
            elif action == 'follow':
                current_user.follows.add(target_profile)
            current_user.save()
        return render(request,'home.html',{'posts':posts})
    else:
        messages.success(request, 'You are not logged in')
        return redirect('welcome')
def post_create(request):
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
    if not request.user.is_authenticated:
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']
            recaptcha_token = request.POST.get('recaptcha_token')
            if not validate_recaptcha(recaptcha_token, "LOGIN"):  # Validate reCAPTCHA
                messages.error(request, 'reCAPTCHA validation failed. Please try again.')
                return redirect('login')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'You have been logged in!')
                return redirect(f'http://localhost:8000/profile/{request.user.profile.user_id}')
            else:
                messages.success(request, 'Something went wrong please try again')
                return redirect('login')
        else:
            return render(request,'login.html')
    else:
        return redirect(f'http://localhost:8000/profile/{request.user.profile.user_id}')

def logout_user(request):
    logout(request)
    messages.success(request, 'You have been logged out')
    return redirect(f'http://localhost:8000/')