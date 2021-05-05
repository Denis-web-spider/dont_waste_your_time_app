from django.urls import path

from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordChangeView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)

from .forms import (
    MyAuthenticationForm,
    MyPasswordChangeForm,
    MyPasswordResetForm,
    MySetPasswordForm,
)

from .views import RegistrationView, UserAccountView


urlpatterns = [
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('login/', LoginView.as_view(authentication_form=MyAuthenticationForm), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('change-password/', PasswordChangeView.as_view(form_class=MyPasswordChangeForm), name='password_change'),
    path('password-reset/', PasswordResetView.as_view(form_class=MyPasswordResetForm), name='password_reset'),
    path('password_reset/done/', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<str:uidb64>/<str:token>/', PasswordResetConfirmView.as_view(form_class=MySetPasswordForm), name='password_reset_confirm'),
    path('reset/done/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('account/', UserAccountView.as_view(), name='user_account')
]
