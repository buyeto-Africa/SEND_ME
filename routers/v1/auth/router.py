from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from core.database import get_db
from sqlalchemy.orm import Session
from models.user import User
from schemas.auth.signup import SignupRequest, SignupResponse
from schemas.auth.login import LoginRequest, LoginResponse
from schemas.auth.token import Token
from core.security import verify_password, create_access_token, get_password_hash

router = APIRouter(tags=["Authentication"])

@router.post("/signup/", response_model=SignupResponse, status_code=201)
async def signup(request: SignupRequest, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash the password
    hashed_password = get_password_hash(request.password)
    
    # Create new user
    new_user = User(
        email=request.email, 
        phone_number=request.phone_number,
        password=hashed_password, 
        tenant_id=request.tenant_id,
        role="customer"  # Default role is customer
    )
    
    # Add user to the database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"msg": "User created successfully"}

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate a user and return a JWT token
    """
    # Find the user by email
    user = db.query(User).filter(User.email == request.email).first()
    
    # Check if user exists and password is correct
    if not user or not verify_password(request.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user"
        )
    
    # Create access token
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "tenant_id": user.tenant_id,
        "role": user.role
    }
    access_token = create_access_token(token_data)
    
    # Return token with user info
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "role": user.role,
        "tenant_id": user.tenant_id
    }

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    OAuth2 compatible token endpoint
    """
    # Find the user by email/username
    user = db.query(User).filter(User.email == form_data.username).first()
    
    # Check if user exists and password is correct
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "tenant_id": user.tenant_id,
        "role": user.role
    }
    access_token = create_access_token(token_data)
    
    # Return token
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }