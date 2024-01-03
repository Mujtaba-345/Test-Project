from django.urls import path
from .views import UserSignUpAPIView, UserProfileAPiView, ConfirmsEmailAPIView, ChangePasswordAPIView, \
    PasswordResetAPIView, PasswordResetConfirmView, ResendEmailAPIView, ProductApIView, ProductDetailApIView, \
    ProductPDFView, ProductCSVAPIView, LogoutView

urlpatterns = [
    path("signup/", UserSignUpAPIView.as_view(), name="signup"),
    path("profile/<int:pk>/", UserProfileAPiView.as_view(), name="user-profile"),
    path("verify-email/<str:token>/", ConfirmsEmailAPIView.as_view(), name="verify_email"),
    path("change-password/", ChangePasswordAPIView.as_view(), name="change_password"),
    path("forgot-password/", PasswordResetAPIView.as_view(), name="reset_password"),
    path("pdf/", ProductPDFView.as_view(), name="pdf"),
    path("csv/", ProductCSVAPIView.as_view(), name="csv"),
    path('logout/', LogoutView.as_view(), name='logout'),

    path(
        "password-reset-confirm/",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "resend-email/",
        ResendEmailAPIView.as_view(),
        name="resend-email",
    ),
    path(
        "products/",
        ProductApIView.as_view(),
        name="get-product",
    ),
    path(
        "products/<int:pk>/",
        ProductDetailApIView.as_view(),
        name="get-product-detail",
    ),

]
