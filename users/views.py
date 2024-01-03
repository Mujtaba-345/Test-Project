from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.views import APIView
from .serializers import UserSignupSerializer, UserProfileSerializer, ChangePasswordSerializer, \
    ForgotPasswordSerializer, PasswordResetConfirmSerializer, ProductSerializer, UserSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import UserProfile, User, Product
from rest_framework.permissions import IsAuthenticated
from utils.utility import send_html_email, encode_token, decode_token
from utils.constants import CLIENT_BASE_URL
from jwt import ExpiredSignatureError, PyJWTError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import MultiPartParser
from rest_framework import generics
from utils.permissions import IsModeratorOrReadOnly
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Image, Table, TableStyle
import csv
from rest_framework import permissions
from rest_framework_simplejwt.tokens import RefreshToken


class UserSignUpAPIView(APIView):
    @swagger_auto_schema(
        operation_id="User SignUp",
        operation_description="User SignUp",
        security=[],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='User username', default="ali"),
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='User email', default="ali@gmail.com"),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='User password', default="1234"),
                # Add other fields as needed
            },
            required=['username', 'email', 'password']
        ),
    )
    def post(self, request):
        data = request.data
        serializer = UserSignupSerializer(data=data)

        try:
            serializer.is_valid(raise_exception=True)

            email_exists = User.objects.filter(email=data.get('email')).exists()
            if email_exists:
                return Response({"error": "Email is already registered.Confirm your email to activate your account"},
                                status=status.HTTP_400_BAD_REQUEST)

            user = serializer.save()

            # Send a welcome email
            UserSignUpAPIView.send_sign_up_email(user)

            payload = {
                "data": serializer.data,
                "description": "Congratulations! "
                               "you are registered successfully. Confirm your email to activate your account"
            }

            return Response(payload, status=status.HTTP_200_OK)

        except serializers.ValidationError as e:
            if 'username' in e.detail:
                e.detail['username'] = [
                    "A user with that username already exists.Confirm your email to activate your account"]

            return Response({"error": e.detail}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @staticmethod
    def send_sign_up_email(user):
        token = encode_token(user.email, 10)
        email_context = {
            "accept_link": f"{CLIENT_BASE_URL}/users/verify-email/{token}/"

        }
        send_html_email(
            to=user.email,
            subject="Welcome to Test Project",
            template="email/welcome_email.html",
            context=email_context,
        )


class UserProfileAPiView(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        operation_id='Update Profile',
        operation_description='Upload Image and address',
        manual_parameters=[
            openapi.Parameter('image', openapi.IN_FORM, type=openapi.TYPE_FILE, description='Image to be uploaded'),
            openapi.Parameter('address', openapi.IN_FORM, type=openapi.TYPE_STRING, description='address',
                              default="address"),
            openapi.Parameter(
                name='id',
                in_=openapi.IN_PATH,
                type=openapi.TYPE_INTEGER,
                description='user id',
                default=1
            ),
        ],
        security=[{"Bearer": []}],  # Ensure this matches your Swagger settings
    )
    def put(self, request, pk=None):
        try:
            # Retrieve the UserProfile instance to update
            profile, created = UserProfile.objects.get_or_create(user_id=pk)

            data = request.data
            serializer = UserProfileSerializer(profile, data=data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                payload = {
                    "data": serializer.data,
                    "description": "Profile updated successfully"
                }
                return Response(payload, status=status.HTTP_200_OK)

        except UserProfile.DoesNotExist:
            return Response({"error": "UserProfile not found"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:

            return Response({"error": "An error occurred during profile update."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ConfirmsEmailAPIView(APIView):
    authentication_classes = ()
    permission_classes = ()

    @swagger_auto_schema(
        operation_id="Email Verification",
        operation_description="Email Verification",
        security=[],
        manual_parameters=[
            # Specify path parameter 'token'
            openapi.Parameter(
                name='token',
                in_=openapi.IN_PATH,
                type=openapi.TYPE_STRING,
                description='The token for email verification',
                default="fhjfjfjjfjfjfjh"
            ),
        ],
    )
    def get(self, request, *args, **kwargs):
        try:
            token = kwargs.get("token")
            if token:
                decrypt_data = decode_token(token)
                user = User.objects.filter(email__iexact=decrypt_data["email"]).first()
                if user:
                    user.is_email_verified = True
                    user.save()
                    return Response({"description": "Your email has been verified! You can proceed to login."},
                                    status=status.HTTP_200_OK)
                return Response({'error': "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            # Handle other exceptions
            return Response({"error": "An error occurred during email confirmation."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChangePasswordAPIView(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        operation_id="Change Password",
        operation_description="Change Password",
        security=[{"Bearer": []}],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'old_password': openapi.Schema(type=openapi.TYPE_STRING, description='User old password',
                                               default="123"),
                'new_password': openapi.Schema(type=openapi.TYPE_STRING, description='User new password',
                                               default="1234"),
            },
            required=['old_password', 'new_password']
        ),
    )
    def post(self, request):
        try:
            user = self.request.user
            serializer = ChangePasswordSerializer(data=request.data)
            if serializer.is_valid():
                old_password = serializer.validated_data.get("old_password")
                new_password = serializer.validated_data.get("new_password")

                if user.check_password(old_password):
                    user.set_password(new_password)
                    user.save()
                    return Response({"description": 'Your password has been updated successfully!.'},
                                    status=status.HTTP_200_OK)
                else:
                    return Response({"error": 'Your old password is not entered correctly'},
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Handle other exceptions"
            return Response({"error": "An error occurred during password change."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PasswordResetAPIView(APIView):
    authentication_classes = ()
    permission_classes = ()

    @swagger_auto_schema(
        operation_id="Forgot Password",
        operation_description="Forgot Password",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='User Email', default="ali@gmail.com"),
            },
            required=['email']
        ),
        security=[],
    )
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user_email = serializer.validated_data.get("email")
            token = encode_token(user_email, 2)
            sent_email = self.send_password_reset_email(user_email, token)
            if sent_email:
                return Response({"description": "Password Reset Link Sent to your email"},
                                status=status.HTTP_200_OK)
            return Response({"error": "Email is not found"}, status=status.HTTP_404_NOT_FOUND)

    @staticmethod
    def send_password_reset_email(user_email, token):
        try:
            user = User.objects.filter(email__iexact=user_email).exists()
            if user:
                email_context = {
                    "reset_link": f'{CLIENT_BASE_URL}/users/password-reset-confirm/?&token={token}',
                    "expiration_time_minutes": 2
                }
                send_html_email(
                    to=user_email,
                    subject="Welcome to Test Project Reset Password",
                    template="email/password_reset.html",
                    context=email_context,
                )
                return True
        except:
            return False


class PasswordResetConfirmView(APIView):

    @swagger_auto_schema(
        operation_id='User Password Reset Confirm',
        operation_description='User Password Reset Confirm',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'new_password': openapi.Schema(type=openapi.TYPE_STRING, description='new password', default="123"),
                'confirm_new_password': openapi.Schema(type=openapi.TYPE_STRING, description='confirm new password',
                                                       default="123"),
            },
            required=['new_password', 'confirm_new_password']
        ),
        manual_parameters=[
            openapi.Parameter('token', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='User Token',
                              default="j8439895rfjfrjejrh"),
        ],
        security=[],  # Ensure this matches your Swagger settings
    )
    def post(self, request, *args, **kwargs):
        token = request.query_params.get('token')
        try:
            decrypt_token = decode_token(token)
            serializer = PasswordResetConfirmSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                user = User.objects.filter(email=decrypt_token["email"]).first()
                if user is not None:
                    user.set_password(serializer.validated_data['new_password'])
                    user.save()
                    return Response({'description': 'Password reset successfully'}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
        except ExpiredSignatureError:
            # Handle the case where the token has expired
            return Response({"error": "Link has been expired"}, status=status.HTTP_400_BAD_REQUEST)
        except PyJWTError:
            # Handle the case where the token is invalid with a custom error response
            return Response({"error": "Invalid token"},
                            status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


class ResendEmailAPIView(APIView):
    authentication_classes = ()
    permission_classes = ()

    @swagger_auto_schema(
        operation_id="Resend Email",
        operation_description="Resend Email",
        security=[],
        manual_parameters=[
            openapi.Parameter('email', in_=openapi.IN_QUERY, description='User email', type=openapi.TYPE_STRING,
                              default="ali@gmail.com"),
        ]
    )
    def get(self, request):
        email = request.query_params.get("email", None)
        try:
            if email:
                user = User.objects.filter(email__iexact=email).first()
                if not user.is_email_verified:
                    UserSignUpAPIView.send_sign_up_email(user)
                    return Response({"description": "Email Sent Successfully"}, status=status.HTTP_200_OK)
                return Response({"description": "User With This Email Is Already Verified"}, status=status.HTTP_200_OK)
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": "An error occurred while resending the email."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProductApIView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsModeratorOrReadOnly,)


class ProductDetailApIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = "pk"
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsModeratorOrReadOnly,)


class ProductPDFView(APIView):
    def get(self, request, *args, **kwargs):
        # Fetch products from the database
        products = Product.objects.all()

        # Create a PDF buffer
        buffer = BytesIO()

        # Create the PDF document using ReportLab
        pdf = SimpleDocTemplate(buffer, pagesize=letter)

        # Custom styles for the document
        styles = getSampleStyleSheet()
        custom_style = ParagraphStyle(
            'CustomStyle',
            parent=styles['BodyText'],
            spaceBefore=30,  # Adjust vertical spacing
            spaceAfter=10,
            leftIndent=50,  # Adjust margin spacing from the left
            leading=15,  # Adjust line spacing
        )
        styles.add(custom_style)

        # Content elements to be included in the PDF
        content = []

        for product in products:
            data = ProductSerializer(product).data

            # Add product information with adjusted spacing
            product_info = [
                ["ID:", str(data['id'])],
                ["Title", data['title']],
                ["Description", data['description']],
                ["Price:", str(data['price'])],
                ["Image:", Image(CLIENT_BASE_URL + data['image'], width=100, height=30)],
            ]

            # Create a Table to arrange the text and image side by side
            table = Table(product_info, colWidths=[100, 100], hAlign='LEFT')
            table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Align content to the top
            ]))

            content.append(table)
            # content.append(Spacer(1, 12))  # Add some space after the table

        # Build the PDF document
        pdf.build(content)

        # File is complete, start the response
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=products.pdf'

        return response


class ProductCSVAPIView(APIView):
    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="mydata.csv"'

        writer = csv.writer(response)
        writer.writerow(["ID", 'Title', 'Description', 'Price'])

        # Fetch data from the database and write it to the CSV file
        my_data = Product.objects.all()
        for data in my_data:
            writer.writerow([data.pk, data.title, data.description, data.price])

        return response


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh_token')

        if not refresh_token:
            return Response({'error': 'refresh_token key is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
